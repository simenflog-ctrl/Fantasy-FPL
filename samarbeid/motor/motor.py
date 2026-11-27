"""Motor: byttesøk, rullerende byttepolitikk, Free Hit, eierbane og alternativtabeller.

Flyttet fra samarbeid/gw10/codex/modell.py linje 292-475 og 482-559 (uten rapporttekst). Algoritmene er uendret;
tall som sto i koden (runde 10, slutt 19, budsjett 995, bank 4, FH 16) er blitt parametre.

Begreper:
  tropp s      : 15 interne indekser sortert på (posisjon, indeks), se lag.py
  sv           : salgsverdi per spiller (tideler); for spillere som ikke eies = kjøpspris
  eierbane     : én gjennomkjøring av hele horisonten med samme byttepolitikk (`bane`)
  byttepolitikk: hver runde vurderes bytter ut fra de neste fire rundene; et gratisbytte må gi mer enn 1 poeng,
                 et betalt bytte mer enn 5 (`rullering`)
  poengsett    : kolonne 0 = codex, kolonne 1 = repo_hybrid. Blanding = vekt*codex + (1-vekt)*repo_hybrid.
"""
import tempfile
from collections import Counter

import numpy as np
import pulp

from lag import LUT, PERMS, FORMS, select, obj_batch
from uke import heltall, vindu_slutt

SETT = ['codex', 'repo_hybrid']
INGEN = -1          # «ingen Bench Boost-kolonne» i funksjonene som tar en BB-kolonne


class Motor:
    def __init__(self, u, pr, ft=2, vekt=.5, bb_runder=None, fh_runder=None, fh_start=None, tmp=None):
        """u: Uke. pr: resultat fra poeng.prognose. ft: gratisbytter nå.

        bb_runder / fh_runder: runder der chipen lovlig kan brukes (tom liste = ikke tilgjengelig), alle i horisonten.
        Standard: BB i alle runder i horisonten, FH fra og med neste runde.
        fh_start: FH-runden som antas mens byttekandidater lages og rangeres (rutenettet finner den beste etterpå).
        """
        # Samme grenser som kjor.kontroller_oppsett, slik at direkte bruk av Motor heller ikke regner stille på
        # ugyldige verdier (Codex' kontroll 21. nov, F1, F2 og F7).
        assert u.slutt <= vindu_slutt(u.g0), \
            'Horisonten (til runde %d) går forbi chipvinduet, som slutter i runde %d' % (u.slutt, vindu_slutt(u.g0))
        assert heltall(ft) is not None and 0 <= heltall(ft) <= 5, 'Gratisbytter må være et heltall 0-5, ikke %r' % (ft,)
        assert np.isfinite(float(vekt)) and 0 <= float(vekt) <= 1, 'Vekten på codex må ligge i [0, 1], ikke %r' % (vekt,)
        self.u = u
        self.g0, self.slutt, self.H, self.N, self.GWS = u.g0, u.slutt, u.H, u.N, u.GWS
        self.POS, self.TEAM, self.COST, self.SALES, self.ORIG = u.POS, u.TEAM, u.COST, u.SALES, u.ORIG
        self.M = np.array([pr.XP, pr.REPO])
        self.vekt = float(vekt)
        self.BLEND = self.bland(self.M)
        self.PP = pr.PP.copy()
        self.UI = pr.UI
        self.ft = heltall(ft)
        # En oppgitt chiprunde utenfor horisonten ble før filtrert bort uten melding (Codex' kontroll 23. nov, F7).
        for navn, runder in (('BB', bb_runder), ('FH', fh_runder)):
            utenfor = sorted(set(g for g in (runder or []) if g not in u.GWS))
            assert not utenfor, '%s-runde %s ligger utenfor horisonten %d-%d' % (navn, utenfor, u.g0, u.slutt)
        self.bb_runder = list(u.GWS) if bb_runder is None else list(bb_runder)
        self.fh_runder = list(u.GWS[1:]) if fh_runder is None else list(fh_runder)
        assert u.g0 not in self.fh_runder, 'Free Hit i inneværende runde er ikke støttet (se plan-v2.md del D)'
        self.fh_start = fh_start if fh_start is not None else (self.fh_runder[0] if self.fh_runder else None)
        assert self.fh_start is None or self.fh_start in self.fh_runder, \
            'fh_start %s er ikke blant de tilgjengelige FH-rundene %s' % (self.fh_start, self.fh_runder)
        self.FH = None
        self.TEMPLATES = []
        self.tmp = tmp or tempfile.gettempdir()

    # ------------------------------------------------------------ små hjelpere

    def bland(self, v):
        """Blanding av de to poengsettene langs første akse (v[0] = codex, v[1] = repo_hybrid)."""
        return self.vekt * v[0] + (1 - self.vekt) * v[1]

    def ordered(self, ss):
        return np.array(sorted(set(int(i) for i in ss), key=lambda i: (self.POS[i], i)), dtype=np.int64)

    def legal(self, s):
        assert len(s) == len(set(s)) == 15
        assert [int(sum(self.POS[s] == k)) for k in range(1, 5)] == [2, 5, 5, 3]
        assert max(Counter(self.TEAM[s]).values()) <= 3

    def tropp_etter(self, ut, inn):
        """Troppen etter å ha solgt `ut` og kjøpt `inn` (ID-er eller entydige navn)."""
        ut = {self.u.finn(x, self.ORIG) for x in ut}
        inn = {self.u.finn(x) for x in inn}
        assert ut <= set(self.ORIG), 'Selger en spiller som ikke er i troppen'
        s = self.ordered((set(self.ORIG) - ut) | inn)
        self.transact(self.ORIG, s, self.SALES, self.u.bank)      # feiler hvis ulovlig eller for dyrt
        return s

    # ------------------------------------------------------------ rask tilnærming og nabosøk

    def approx(self, ss, pred, pp, cols, bb=INGEN):
        """Rask, omtrentlig verdi av mange tropper (brukes bare til å sile kandidater; aldri til sluttall)."""
        ss = np.atleast_2d(ss)
        v = pred[ss][:, :, cols]
        ap = pp[ss][:, :, cols]
        cs = []
        chosenpp = []
        for sl in [slice(0, 2), slice(2, 7), slice(7, 12), slice(12, 15)]:
            order = np.argsort(-v[:, sl, :], axis=1)
            a = np.take_along_axis(v[:, sl, :], order, axis=1)
            p = np.take_along_axis(ap[:, sl, :], order, axis=1)
            cs.append(np.concatenate([np.zeros((len(ss), 1, len(cols))), np.cumsum(a, axis=1)], axis=1))
            chosenpp.append(np.concatenate([np.zeros((len(ss), 1, len(cols))), np.cumsum(1 - p, axis=1)], axis=1))
        best = np.zeros((len(ss), len(cols)))
        tot = v.sum(axis=1)
        cap = v.max(axis=1)
        for d, m, f in FORMS:
            xi = cs[0][:, 1] + cs[1][:, d] + cs[2][:, m] + cs[3][:, f]
            absent = chosenpp[1][:, d] + chosenpp[2][:, m] + chosenpp[3][:, f]
            benchpts = tot - xi - (cs[0][:, 2] - cs[0][:, 1])
            gain = benchpts * np.minimum(absent, 3) / 3 + (cs[0][:, 2] - cs[0][:, 1]) * chosenpp[0][:, 1]
            z = xi + cap + gain
            if bb in cols:
                z[:, cols.index(bb)] = tot[:, cols.index(bb)] + cap[:, cols.index(bb)]
            best = np.maximum(best, z)
        return best.sum(axis=1)

    def pools(self, pred, cols, avail):
        """Kjøpskandidater per posisjon: de 12 beste over `cols` og de 4 billigste."""
        UI, POS, COST = self.UI, self.POS, self.COST
        result = []
        for k in range(1, 5):
            q = UI[(POS[UI] == k) & avail[UI]]
            v = pred[q][:, cols].sum(axis=1)
            top = q[np.argsort(-v, kind='stable')[:12]]
            cheap = q[np.lexsort((q, COST[q]))[:4]]
            result.append(np.array(sorted(set(top) | set(cheap)), dtype=np.int64))
        return result

    def neighbors(self, s, ps, sv, liquid):
        """Alle lovlige tropper som er ett bytte unna s, med kjøp fra ps (liste per posisjon)."""
        POS, TEAM = self.POS, self.TEAM
        ss = []
        clubs = np.bincount(TEAM[s], minlength=int(TEAM.max()) + 1)
        spent = sv[s].sum()
        for slot, out in enumerate(s):
            inc = ps[POS[out] - 1]
            inc = inc[~np.isin(inc, s)]
            inc = inc[(spent - sv[out] + sv[inc] <= liquid) & (clubs[TEAM[inc]] - (TEAM[inc] == TEAM[out]) < 3)]
            for p in inc:
                new = s.copy()
                new[slot] = p
                ss.append(self.ordered(new))
        return np.array(ss, dtype=np.int64) if ss else np.empty((0, 15), dtype=np.int64)

    def transact(self, s, new, sv, cash):
        """Gjennomfør byttene fra s til new. Returnerer (ny tropp, nye salgsverdier, ny bank)."""
        self.legal(new)
        out = set(s) - set(new)
        inn = set(new) - set(s)
        cash = int(cash + sum(sv[i] for i in out) - sum(self.COST[i] for i in inn))
        assert cash >= 0, 'Ikke råd til byttene'
        sv = sv.copy()
        for i in out | inn:
            sv[i] = self.COST[i]
        return new, sv, cash

    # ------------------------------------------------------------ byttepolitikk

    def rullering(self, g, s, sv, cash, ft, pred, pp, avail, wc=None):
        """Byttepolitikken i runde g: se fire runder fram, gjør bytter som lønner seg. (gw10: `rolling`)

        Returnerer (tropp, salgsverdier, bank, antall bytter, poengtrekk).
        """
        g0, S = self.g0, self.slutt
        end = min(S, g + 3, wc - 1 if (wc and wc > g) else S)
        cols = [h - g0 for h in range(g, end + 1) if h != self.FH]
        n = hits = 0
        if not cols:
            return s, sv, cash, n, hits
        for _ in range(min(5, ft + 1)):
            ps = self.pools(pred, cols, avail)
            liquid = int(cash + sv[s].sum())
            nn = self.neighbors(s, ps, sv, liquid)
            if not len(nn):
                break
            ap = self.approx(nn, pred, pp, cols)
            first = np.argsort(-ap)[:3]
            # Par der det første byttet finansierer det andre.
            if n < ft:
                extra = []
                for j in first:
                    for q in self.neighbors(nn[j], ps, sv, liquid):
                        if len(set(q) - set(s)) == 2:
                            extra.append(q)
                if extra:
                    nn = np.concatenate([nn, np.array(extra)])
            nn = np.unique(nn, axis=0)
            ap = self.approx(nn, pred, pp, cols)
            counts = np.array([len(set(q) - set(s)) for q in nn])
            valid = counts <= ft - n + 1
            nn = nn[valid]
            ap = ap[valid]
            counts = counts[valid]
            costhit = 4 * np.maximum(0, counts - (ft - n))
            rank = np.argsort(-(ap - costhit))
            short = nn[rank[:3]]
            counts = counts[rank[:3]]
            base = obj_batch(s[None, :], pred, pp, np.array(cols), INGEN, self.POS, LUT, PERMS)[0]
            vv = obj_batch(short, pred, pp, np.array(cols), INGEN, self.POS, LUT, PERMS)
            scores = vv - 4 * np.maximum(0, counts - (ft - n))
            j = scores.argmax()
            cnt = int(counts[j])
            gain = vv[j] - base
            paid = max(0, cnt - (ft - n))
            free = cnt - paid
            threshold = (0 if ft - n == 5 or g == S else free) + 5 * paid
            if gain <= threshold + 1e-7:
                break
            s, sv, cash = self.transact(s, short[j], sv, cash)
            n += cnt
            hits += 4 * paid
            if paid:
                break
        return s, sv, cash, n, hits

    def ny_tropp(self, g, s, sv, cash, pred, pp, avail, fh=False, ban=None, keep=None):
        """Bygg en helt ny tropp i runde g. fh=True: Free Hit (bare runde g teller). (gw10: `renew`)

        fh=False er wildcard-grenen fra gw09/gw10. Den er flyttet, men ikke brukt eller testet ennå.
        """
        g0, UI, POS, TEAM = self.g0, self.UI, self.POS, self.TEAM
        cols = list(range(g - g0, self.H)) if not fh else [g - g0]
        cols = [t for t in cols if fh or self.FH is None or t != self.FH - g0]
        ps = self.pools(pred, cols, avail)
        liquid = int(cash + sv[s].sum())
        seeds = []

        def repair(template):
            cur = list(template)
            used = set(cur)
            clubs = Counter(TEAM[cur])
            for slot, i in enumerate(cur):
                if (avail[i] or i in s) and i != ban:
                    continue
                used.remove(i)
                clubs[TEAM[i]] -= 1
                cand = [int(z) for z in UI if avail[z] and POS[z] == POS[i] and z not in used and z != ban and clubs[TEAM[z]] < 3]
                if not cand:
                    return None
                z = min(cand, key=lambda j: (sv[j], j))
                cur[slot] = z
                used.add(z)
                clubs[TEAM[z]] += 1
            a = self.ordered(cur)
            if sv[a].sum() > liquid:
                return None
            return a

        for q in [s] + self.TEMPLATES:
            a = repair(q)
            if a is not None:
                seeds.append(a)
        cheap = []
        clubs = Counter()
        for k, n in [(1, 2), (2, 5), (3, 5), (4, 3)]:
            for i in sorted([int(z) for z in UI if POS[z] == k and avail[z] and z != ban], key=lambda z: (sv[z], z)):
                if clubs[TEAM[i]] < 3:
                    cheap.append(i)
                    clubs[TEAM[i]] += 1
                    if sum(POS[z] == k for z in cheap) == n:
                        break
        if len(cheap) == 15 and sv[cheap].sum() <= liquid:
            seeds.append(self.ordered(cheap))
        if keep is not None:
            seeds = [a for a in seeds if keep in a]
        assert seeds
        ss = np.unique(np.array(seeds), axis=0)
        ap = self.approx(ss, pred, pp, cols)
        ss = ss[np.argsort(-ap)[:4]]
        vv = obj_batch(ss, pred, pp, np.array(cols), INGEN, POS, LUT, PERMS)
        best = ss[vv.argmax()].copy()
        value = vv.max()
        for _ in range(3):
            nn = self.neighbors(best, ps, sv, liquid)
            if ban is not None:
                nn = nn[~np.any(nn == ban, axis=1)]
            if keep is not None:
                nn = nn[np.any(nn == keep, axis=1)]
            if not len(nn):
                break
            ap = self.approx(nn, pred, pp, cols)
            nn = nn[np.argsort(-ap)[:3]]
            vv = obj_batch(nn, pred, pp, np.array(cols), INGEN, POS, LUT, PERMS)
            j = vv.argmax()
            if vv[j] <= value + 1e-7:
                break
            best = nn[j].copy()
            value = vv[j]
        self.legal(best)
        assert all(avail[i] or i in s for i in best)
        if ban is not None:
            assert ban not in best
        return self.ordered(best)

    def heltallsforslag(self, runder, nmoves=None, model=2, bb=None):
        """Heltallsoptimering som FORESLÅR en tropp (gw10: `seed`). Alle sluttall regnes med eksakte autobytter.

        runder: rundene som teller. nmoves: nøyaktig antall bytter fra dagens tropp (None = fri tropp, for Free Hit).
        model: 0 = codex, 1 = repo_hybrid, 2 = blanding.
        """
        POS, TEAM, ORIG, g0 = self.POS, self.TEAM, self.ORIG, self.g0
        candidates = sorted(set(self.UI) | set(ORIG)) if nmoves is not None else list(self.UI)
        pred = self.BLEND if model == 2 else self.M[model]
        prob = pulp.LpProblem('motor', pulp.LpMaximize)
        x = pulp.LpVariable.dicts('s', candidates, cat='Binary')
        price = self.SALES.copy()
        for k, n in [(1, 2), (2, 5), (3, 5), (4, 3)]:
            prob += pulp.lpSum(x[i] for i in candidates if POS[i] == k) == n
        for t in self.u.T:
            prob += pulp.lpSum(x[i] for i in candidates if TEAM[i] == t) <= 3
        prob += pulp.lpSum(int(price[i]) * x[i] for i in candidates) <= self.u.budsjett
        if nmoves is not None:
            prob += pulp.lpSum(x[i] for i in candidates if i not in ORIG) == nmoves
        obj = []
        for g in runder:
            y = pulp.LpVariable.dicts('xi' + str(g), candidates, cat='Binary')
            c = pulp.LpVariable.dicts('c' + str(g), candidates, cat='Binary')
            prob += pulp.lpSum(y.values()) == 11
            prob += pulp.lpSum(c.values()) == 1
            for i in candidates:
                prob += y[i] <= x[i]
                prob += c[i] <= y[i]
            for k, lo, hi in [(1, 1, 1), (2, 3, 5), (3, 2, 5), (4, 1, 3)]:
                prob += pulp.lpSum(y[i] for i in candidates if POS[i] == k) >= lo
                prob += pulp.lpSum(y[i] for i in candidates if POS[i] == k) <= hi
            obj.extend(float(pred[i, g - g0]) * ((x[i] if bb == g else y[i]) + c[i]) for i in candidates)
        prob += pulp.lpSum(obj)
        solver = pulp.PULP_CBC_CMD(msg=False, timeLimit=8, gapRel=.0001, threads=1)
        solver.tmpDir = str(self.tmp)
        prob.solve(solver)
        s = self.ordered(i for i in candidates if x[i].value() is not None and x[i].value() > .5)
        self.legal(s)
        assert self.SALES[s].sum() <= self.u.budsjett
        if nmoves is not None:
            assert len(set(s) - set(ORIG)) == nmoves
        return s

    def lag_maler(self):
        """Free Hit-maler: beste frie tropp per runde i hvert poengsett. Må kjøres før `bane` med FH."""
        if self.TEMPLATES or not self.fh_runder:
            return
        for g in self.GWS[1:]:
            self.TEMPLATES.extend([self.heltallsforslag([g], model=m) for m in [0, 1, 2]])

    # ------------------------------------------------------------ eierbane

    def bane(self, initial, ft0=None, fh=None, world=None, full=False, arrays=None, record=True):
        """Kjør hele horisonten fra troppen `initial` (troppen ETTER rundens bytter). (gw10: `trajectory`)

        Samme byttepolitikk i alle senere runder. Bench Boost påvirker verken eierskap eller bytter, så én
        bane gir totalen for ALLE BB-runder (`alle_BB[runde - g0]` = [codex, repo_hybrid] med BB den runden).
        fh    : Free Hit-runde eller None
        world : skadeverden (H, N): world[t, i] = første kolonne spilleren igjen er tilgjengelig, sett fra runde t
        full  : True = uttømmende elleversøk (hovedtabeller), False = kort liste (simulering)
        arrays: alternative poengsett (2, N, H), ellers motorens
        """
        g0, H, N, GWS, POS = self.g0, self.H, self.N, self.GWS, self.POS
        assert fh is None or fh in GWS[1:], 'FH må ligge i horisonten og ikke i første runde'
        assert fh is None or fh in self.fh_runder, 'Free Hit i runde %s er ikke tilgjengelig (FH: %s)' % (fh, self.fh_runder)
        if ft0 is None:
            ft0 = self.ft
        else:
            assert heltall(ft0) is not None and 0 <= heltall(ft0) <= 5, 'Gratisbytter må være et heltall 0-5, ikke %r' % (ft0,)
            ft0 = heltall(ft0)
        self.FH = fh
        mats = self.M if arrays is None else arrays
        blend = self.bland(mats)
        s = self.ORIG.copy()
        sv = self.SALES.copy()
        cash = self.u.bank
        ft = ft0
        rr = []
        normal = []
        boost = []
        if world is None:
            world = np.zeros((H, N), dtype=np.int16)
        for t, g in enumerate(GWS):
            release = world[t]
            av = release <= t
            known = (np.arange(H)[None, :] >= release[:, None]) | av[:, None]
            pred = blend * known
            pp = self.PP * known
            before = s.copy()
            ftbefore = ft
            hit = n = 0
            if t == 0:
                n = len(set(initial) - set(s))
                s, sv, cash = self.transact(s, initial, sv, cash)
                active = s
                hit = 4 * max(0, n - ft)
            elif g == fh:
                active = self.ny_tropp(g, s, sv, cash, pred, pp, av, fh=True)
            else:
                s, sv, cash, n, hit = self.rullering(g, s, sv, cash, ft, pred, pp, av)
                active = s
            z = select(active, pred[:, t], pp[:, t], POS, LUT, PERMS, full, False)
            zb = select(active, pred[:, t], pp[:, t], POS, LUT, PERMS, False, True)
            points = (mats[:, active, t] * known[active, t][None, :] * z[1][None, :]).sum(axis=1) - hit
            boosted = (mats[:, active, t] * known[active, t][None, :] * zb[1][None, :]).sum(axis=1) - hit
            rawbench = (mats[:, active[z[3]], t] * known[active[z[3]], t][None, :]).sum(axis=1)
            normal.append(points)
            boost.append(boosted - points)
            if g != fh:
                ft = min(5, max(0, ft - n) + 1)
            if record:
                ids = self.u.ids
                rr.append(dict(gw=g, chip='FH' if g == fh else '', tropp=[ids[i] for i in active],
                               permanent=[ids[i] for i in s], elleve=[ids[active[j]] for j in z[2]],
                               benk=[ids[active[j]] for j in z[3]], kaptein=ids[active[z[4]]],
                               visekaptein=ids[active[z[5]]], vekter=z[1].tolist(), bb_vekter=zb[1].tolist(),
                               poeng=points.tolist(), bb_gevinst=(boosted - points).tolist(),
                               benk_brutto=rawbench.tolist(), inn=[ids[i] for i in sorted(set(active) - set(before))],
                               ut=[ids[i] for i in sorted(set(before) - set(active))], bank=cash / 10,
                               FT_for=ftbefore, FT_etter=ft, trekk=hit))
            self.legal(s)
            assert cash >= 0 and 1 <= ft <= 5
        normal = np.array(normal)
        boost = np.array(boost)
        totals = normal.sum(axis=0)[None, :] + boost
        if fh is not None:
            totals[fh - g0] = np.nan
        return dict(FH=fh, FT=ft0, total_uten_BB=normal.sum(axis=0).tolist(), alle_BB=totals.tolist(),
                    normal=normal.tolist(), boost=boost.tolist(), rows=rr)

    def total(self, p, bb):
        """[codex, repo_hybrid] for banen p med Bench Boost i runde bb (None = uten BB)."""
        return np.array(p['total_uten_BB'] if bb is None else p['alle_BB'][bb - self.g0])

    def velg_bb(self, p):
        """Beste lovlige BB-runde for banen p etter blandingen, eller None hvis BB ikke er tilgjengelig."""
        kand = [g for g in self.bb_runder if g != p['FH']]
        if not kand:
            return None
        return max(kand, key=lambda g: (self.bland(self.total(p, g)), -g))

    def alternativ(self, label, p, bb, gruppe=None):
        """Én rad til alternativer.csv for banen p med BB i runde bb. (gw10: `alternative`)"""
        g0, H = self.g0, self.H
        r = p['rows'][0]
        points = np.array(p['normal']).copy()
        if bb is not None:
            assert bb in self.bb_runder, 'Bench Boost i runde %s er ikke tilgjengelig' % bb
            assert bb != p['FH'], 'Bench Boost og Free Hit kan ikke brukes i samme runde (%s)' % bb
            points[bb - g0] += p['boost'][bb - g0]
        z = dict(alternativ=label, gruppe=gruppe or label[0], FT=p['FT'], BB=bb if bb is not None else '',
                 FH=p['FH'] if p['FH'] is not None else '',
                 ut=self.u.navn(self.u.ix[i] for i in r['ut']), inn=self.u.navn(self.u.ix[i] for i in r['inn']),
                 ut_id=' '.join(str(i) for i in r['ut']), inn_id=' '.join(str(i) for i in r['inn']),
                 poengtrekk_runde=r['trekk'], poengtrekk_totalt=sum(q['trekk'] for q in p['rows']), bank_etter=r['bank'])
        for m, sett in enumerate(SETT):
            for suffix, n in [('runde', 1), ('4r', min(4, H)), ('horisont', H)]:
                z[sett + '_' + suffix] = float(points[:n, m].sum())
        z['blend_horisont'] = float(self.bland([z['codex_horisont'], z['repo_hybrid_horisont']]))
        z['modellspredning'] = abs(z['codex_horisont'] - z['repo_hybrid_horisont'])
        return z

    # ------------------------------------------------------------ sammensatte kjøringer

    def kandidater(self, maks_bytter=4):
        """Foreslå konkrete tropper med 0..maks_bytter bytter. Returnerer {antall bytter: [tropper]}.

        Heltallsforslag over tre horisonter og tre poengsett, pluss alle enkeltbytter og finansieringspar,
        silt med den raske tilnærmingen. Dette er forslag; rangeringen skjer i `standardanalyse`.
        """
        g0, H, GWS, POS, UI, ORIG, SALES = self.g0, self.H, self.GWS, self.POS, self.UI, self.ORIG, self.SALES
        budsjett = self.u.budsjett
        candidates = {0: [ORIG]}
        for n in range(1, maks_bytter + 1):
            seeds = []
            for runder in [[g0], GWS[:4], GWS]:
                for model in [0, 1, 2]:
                    seeds.append(self.heltallsforslag(runder, n, model))
            candidates[n] = list(np.unique(np.array(seeds), axis=0))
        allpools = [UI[POS[UI] == k] for k in range(1, 5)]
        fhcol = None if self.fh_start is None else self.fh_start - g0
        colsets = [[0], list(range(min(4, H))), [t for t in range(H) if t != fhcol]]
        singles = self.neighbors(ORIG, allpools, SALES, budsjett)
        if maks_bytter >= 1 and len(singles):
            for pred in [self.M[0], self.M[1], self.BLEND]:
                for cols in colsets:
                    ap = self.approx(singles, pred, self.PP, cols)
                    candidates[1].extend(singles[np.argsort(-ap)[:5]])
            candidates[1] = list(np.unique(np.array(candidates[1]), axis=0))
        if maks_bytter >= 2:
            pairs = []
            for one in candidates[1]:
                pairs.extend(q for q in self.neighbors(one, allpools, SALES, budsjett) if len(set(q) - set(ORIG)) == 2)
            if pairs:
                pairs = np.unique(np.array(pairs), axis=0)
                for pred in [self.M[0], self.M[1], self.BLEND]:
                    for cols in colsets:
                        ap = self.approx(pairs, pred, self.PP, cols)
                        candidates[2].extend(pairs[np.argsort(-ap)[:5]])
                candidates[2] = list(np.unique(np.array(candidates[2]), axis=0))
        return candidates

    @staticmethod
    def etikett(n):
        return 'A' if n == 0 else 'B' if n == 1 else 'C' if n == 2 else 'D' + str(n)

    def standardanalyse(self, maks_bytter=4, logg=print):
        """Hele den faste analysen (gw10 `main` uten rapport, Groß-test og skadesimulering).

        Returnerer dict med: kandidater, byttesok (rader), valgt {antall bytter: tropp}, rutenett (rader),
        fh (beste FH-runde i rutenettet), planer {A, B, C, D3, D4: bane}, valg (beste etikett), bb,
        alternativer (rader, gruppe A-G), kapteiner (rader), fh_planer, kollisjon.
        """
        g0, GWS, ORIG = self.g0, self.GWS, self.ORIG
        candidates = self.kandidater(maks_bytter)
        logg('Kandidater per antall bytter: ' + str({n: len(v) for n, v in candidates.items()}))
        self.lag_maler()
        chosen = {}
        sokrader = []
        for n, ss in candidates.items():
            ranked = []
            for s in ss:
                p = self.bane(s, fh=self.fh_start)
                bb = self.velg_bb(p)
                score = self.bland(self.total(p, bb))
                ranked.append((score, s, p))
                sokrader.append(dict(bytter=n, ut=self.u.navn(set(ORIG) - set(s)), inn=self.u.navn(set(s) - set(ORIG)),
                                     BB=bb if bb is not None else '', score=score))
            ranked.sort(key=lambda z: -z[0])
            chosen[n] = ranked[0][1]
        # Rutenett: alle lovlige par av FH- og BB-runde for hvert antall bytter, samme politikk i hver celle.
        fh_liste = self.fh_runder or [None]
        bb_liste = self.bb_runder or [None]
        joint = []
        for n, s in chosen.items():
            for fh in fh_liste:
                p = self.bane(s, fh=fh)
                for bb in bb_liste:
                    if bb is None or bb != fh:
                        v = self.total(p, bb)
                        joint.append(dict(bytter=n, FH=fh if fh is not None else '', BB=bb if bb is not None else '',
                                          codex=v[0], repo_hybrid=v[1], blend=self.bland(v)))
        fh = max(joint, key=lambda r: r['blend'])['FH']
        fh = None if fh == '' else fh
        logg('Rutenett ferdig; beste FH: ' + str(fh))
        planer = {self.etikett(n): self.bane(s, fh=fh, full=True) for n, s in chosen.items()}
        valg = max(planer, key=lambda k: self.bland(self.total(planer[k], self.velg_bb(planer[k]))))
        valg_n = next(n for n in chosen if self.etikett(n) == valg)
        selected = planer[valg]
        bb = self.velg_bb(selected)
        alts = [self.alternativ(k, p, self.velg_bb(p)) for k, p in planer.items()]
        # E: valgt handling med hver BB-runde. F: valgt handling med hver FH-runde.
        for g in self.bb_runder:
            if g != fh:
                alts.append(self.alternativ('E_BB' + str(g), selected, g, 'E'))
        fh_planer = {}
        for f in self.fh_runder:
            p = self.bane(chosen[valg_n], fh=f, full=True)
            fh_planer[str(f)] = p
            alts.append(self.alternativ('F_FH' + str(f), p, self.velg_bb(p), 'F'))
        # G: de fire beste kapteinsvalgene på nøyaktig den valgte elleveren.
        kapteiner = self.kapteintabell(selected, bb)
        for k in kapteiner:
            row = self.alternativ('G_' + k['navn'], selected, bb, 'G')
            for m, sett in enumerate(SETT):
                for suff in ['runde', '4r', 'horisont']:
                    row[sett + '_' + suff] += k['_delta'][m]
            row['blend_horisont'] = float(self.bland([row['codex_horisont'], row['repo_hybrid_horisont']]))
            row['modellspredning'] = abs(row['codex_horisont'] - row['repo_hybrid_horisont'])   # arvet gw10-feil
            alts.append(row)
        # BB i samme runde som beste FH: flytt FH til en reserverunde i begge sammenligningsbanene.
        kollisjon = None
        andre = [g for g in self.fh_runder if g != fh]
        if fh is not None and andre and fh in self.bb_runder:
            backup = self.fh_start if self.fh_start in andre else (fh - 1 if (fh - 1) in andre else andre[0])
            supplement = self.bane(chosen[valg_n], fh=backup, full=True)
            alts.append(self.alternativ('E_BB%d_FH%d' % (fh, backup), supplement, fh, 'E'))
            if g0 in self.bb_runder:
                alts.append(self.alternativ('E_BB%d_FH%d' % (g0, backup), supplement, g0, 'E'))
            kollisjon = dict(BB=fh, FH=backup, plan=supplement)
        for k in kapteiner:
            del k['_delta']
        return dict(kandidater=candidates, byttesok=sokrader, valgt=chosen, rutenett=joint, fh=fh, planer=planer,
                    valg=valg, valg_n=valg_n, bb=bb, alternativer=alts, kapteiner=kapteiner, fh_planer=fh_planer,
                    kollisjon=kollisjon)

    def kapteintabell(self, p, bb, antall=4):
        """De `antall` beste kapteinene (med beste vise) på elleveren i første runde av banen p."""
        u, M, PP, BLEND, g0 = self.u, self.M, self.PP, self.BLEND, self.g0
        r = p['rows'][0]
        s = self.ordered(u.ix[i] for i in r['tropp'])
        z = select(s, BLEND[:, 0], PP[:, 0], self.POS, LUT, PERMS, True, bb == g0)
        xi = z[2]
        caps = []
        for c in xi:
            v = max([j for j in xi if j != c], key=lambda j: BLEND[s[j], 0])
            extra = M[:, s[c], 0] + (1 - PP[s[c], 0]) * M[:, s[v], 0]
            caps.append((float(self.bland(extra)), int(c), int(v), extra))
        caps.sort(key=lambda t: t[:3], reverse=True)
        oldextra = M[:, s[z[4]], 0] + (1 - PP[s[z[4]], 0]) * M[:, s[z[5]], 0]
        rader = []
        for _, c, v, extra in caps[:antall]:
            e = u.E[u.ids[s[c]]]
            rader.append(dict(id=u.ids[s[c]], navn=e['web_name'], vise=u.E[u.ids[s[v]]]['web_name'],
                              codex=M[0, s[c], 0], repo_hybrid=M[1, s[c], 0], p_spiller=PP[s[c], 0],
                              ekstrakopi_codex=extra[0], ekstrakopi_repo=extra[1],
                              ekstrakopi_blend=float(self.bland(extra)), _delta=(extra - oldextra).tolist()))
        return rader

    def faste_planer(self, tropper, bb, fh, ft0=None, full=True):
        """Samme chipdatoer for alle alternativer (gw10 runde 2). tropper: {navn: tropp}. Returnerer (baner, rader)."""
        assert fh is None or fh in self.fh_runder, 'Free Hit i runde %s er ikke tilgjengelig' % fh
        self.lag_maler()
        planer = {k: self.bane(s, ft0=ft0, fh=fh, full=full) for k, s in tropper.items()}
        return planer, [self.alternativ(k, p, bb, k) for k, p in planer.items()]

    def rutenett_for(self, tropper):
        """Chiprutenett for vilkårlige tropper ({navn: tropp}), f.eks. Claudes egne alternativer.

        Samme regning som rutenettet i `standardanalyse`: alle lovlige par av FH- og BB-runde, samme byttepolitikk i
        hver celle. Gir hvert alternativ sin egen beste chipdato, ikke bare de felles datoene (Codex' kontroll, F11).
        """
        self.lag_maler()
        rader = []
        for navn, s in tropper.items():
            n = len(set(s) - set(self.ORIG))
            for fh in self.fh_runder or [None]:
                p = self.bane(s, fh=fh)
                for bb in self.bb_runder or [None]:
                    if bb is None or bb != fh:
                        v = self.total(p, bb)
                        rader.append(dict(alternativ=navn, bytter=n, FH=fh if fh is not None else '',
                                          BB=bb if bb is not None else '', codex=v[0], repo_hybrid=v[1], blend=self.bland(v)))
        return rader

    def ft_folsomhet(self, tropper, bb, fh, ft_verdier):
        """Alternativtabellen på nytt for andre antall gratisbytter."""
        rader = []
        for ft0 in ft_verdier:
            for k, s in tropper.items():
                rader.append(self.alternativ(k, self.bane(s, ft0=ft0, fh=fh, full=True), bb, k))
        return rader

    def kontroller_bane(self, p):
        """Regn banen på nytt fra spillerpoeng og vekter, og kontroller lovlighet. Returnerer største avvik."""
        u, g0 = self.u, self.g0
        feil = 0.
        for r in p['rows']:
            s = np.array([u.ix[i] for i in r['tropp']])
            self.legal(s)
            v = (self.M[:, s, r['gw'] - g0] * np.array(r['vekter'])[None, :]).sum(axis=1) - r['trekk']
            feil = max(feil, float(np.abs(v - np.array(r['poeng'])).max()))
        return feil
