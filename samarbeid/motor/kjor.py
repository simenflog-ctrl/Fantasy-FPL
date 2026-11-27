#!/usr/bin/env python3
"""Ukemotoren fra kommandolinjen. Se README.md.

    python samarbeid/motor/kjor.py samarbeid/gwNN --frys      # kopier repoets poengfiler til gwNN/motor/input/
    python samarbeid/motor/kjor.py samarbeid/gwNN             # hele kjøringen
    python samarbeid/motor/kjor.py samarbeid/gwNN --bare-poeng

Leser gwNN/motor/oppsett.json og gwNN/data/. Skriver bare i gwNN/motor/ (eller --ut). Ingen nett.
Motoren skriver tall, ikke anbefalinger.
"""
import argparse
import hashlib
import shutil
import sys
import time
from pathlib import Path

HER = Path(__file__).resolve().parent
sys.path.insert(0, str(HER))

import numpy as np  # noqa: E402

import poeng  # noqa: E402
import skadesim  # noqa: E402
from motor import Motor  # noqa: E402
from uke import KINDS, Uke, heltall, les_json, skriv_csv, skriv_json, vindu_slutt  # noqa: E402

FRYSES = ['player_matches.csv', 'expected_points.csv']


def frys(uke_mappe):
    """Kopier repoets data/derived-filer til gwNN/motor/input/. Nekter å overskrive.

    Kilden er repoet ukemappen ligger i (gwNN/../..), ikke repoet motoren kjøres fra, slik at en motor fra en annen
    arbeidskopi ikke fryser gamle filer.
    """
    kilde = uke_mappe.parents[1] / 'data' / 'derived'
    mal = uke_mappe / 'motor' / 'input'
    for fn in FRYSES:
        if not (kilde / fn).exists():
            raise SystemExit('Finner ikke %s' % (kilde / fn))
        if (mal / fn).exists():
            raise SystemExit('Finnes allerede, overskriver ikke: ' + str(mal / fn))
    mal.mkdir(parents=True, exist_ok=True)
    for fn in FRYSES:
        shutil.copy2(kilde / fn, mal / fn)
        print('Frosset', mal / fn)


def kontroller_oppsett(o, uke_mappe=None):
    """Stopp med en tydelig feilmelding på oppsett motoren ellers ville regnet feil på uten å si fra.

    Funnet av Codex i kontrollene 19. og 21. november: ukjente chips, felles BB/FH utenfor vinduet eller i samme runde,
    horisont over chipvinduet, en oppgitt overstyringsfil som ikke finnes, `fh_start` uten tilgjengelig Free Hit (F1),
    og gratisbytter, FT-følsomhet eller vekt som ikke er lovlige tall (F2; 1,9 gratisbytter ble før regnet som 1).
    """
    feil = ['mangler «%s»' % k for k in ('runde', 'gratisbytter') if k not in o]
    if feil:
        raise ValueError('Feil i oppsett.json: ' + '; '.join(feil))
    runde = heltall(o['runde'])
    if runde is None or not 1 <= runde <= 38:
        raise ValueError('Feil i oppsett.json: runde må være et heltall 1-38, ikke %r' % (o['runde'],))
    vindu = vindu_slutt(runde)
    ft = heltall(o['gratisbytter'])
    if ft is None or not 0 <= ft <= 5:
        feil.append('gratisbytter må være et heltall 0-5, ikke %r' % (o['gratisbytter'],))
    for v in o.get('ft_folsomhet') or []:
        if heltall(v) is None or not 0 <= heltall(v) <= 5:
            feil.append('ft_folsomhet: %r er ikke et heltall 0-5' % (v,))
    vekt = o.get('vekt_codex', .5)
    try:
        vekt_ok = bool(np.isfinite(float(vekt)) and 0 <= float(vekt) <= 1) and not isinstance(vekt, bool)
    except (TypeError, ValueError):
        vekt_ok = False
    if not vekt_ok:
        feil.append('vekt_codex må være et tall i [0, 1], ikke %r' % (vekt,))
    if heltall(o.get('maks_bytter', 4)) is None or heltall(o.get('maks_bytter', 4)) < 0:
        feil.append('maks_bytter må være et heltall >= 0')
    h = o.get('horisont_til')
    if h is not None and (heltall(h) is None or not runde <= heltall(h) <= vindu):
        feil.append('horisont_til %s må ligge i %d-%d (chipvinduet slutter i runde %d)' % (h, runde, vindu, vindu))
    slutt = heltall(h) if h is not None and heltall(h) is not None else min(runde + 9, vindu)
    chips = o.get('chips') or {}
    andre = sorted(set(chips) - {'BB', 'FH'})
    if andre:
        feil.append('chips %s støttes ikke; bare BB og FH (Wildcard og Triple Captain: plan-v2.md del D)' % andre)
    # Chiprundene må ligge i horisonten, ikke bare i chipvinduet: Motor filtrerte før bort runder etter horisonten
    # uten melding (Codex' kontroll 23. nov, F7).
    for c in ('BB', 'FH'):
        for g in chips.get(c) or []:
            if heltall(g) is None or not runde <= heltall(g) <= min(slutt, vindu):
                feil.append('chips %s: %r er ikke en runde i horisonten %d-%d' % (c, g, runde, min(slutt, vindu)))
    if runde in (chips.get('FH') or []):
        feil.append('Free Hit i inneværende runde (%d) støttes ikke' % runde)
    fs = o.get('fh_start')
    if fs is not None:
        if heltall(fs) is None or not runde < heltall(fs) <= slutt:
            feil.append('fh_start %r må være en runde etter inneværende og innenfor horisonten (%d-%d)' % (fs, runde + 1, slutt))
        elif 'FH' in chips and heltall(fs) not in chips['FH']:
            feil.append('fh_start %s er ikke blant chips FH %s (Free Hit er ikke tilgjengelig den runden)' % (fs, chips['FH']))
    ss = o.get('skadesim') or {}
    if heltall(ss.get('trekk', 200)) is None or heltall(ss.get('trekk', 200)) < 0:
        feil.append('skadesim trekk må være et heltall >= 0')
    for r in ss.get('rater', [.01, .02]):
        try:
            rate_ok = 0 < float(r) < 1
        except (TypeError, ValueError):
            rate_ok = False
        if not rate_ok:
            feil.append('skadesim rater: %r må ligge mellom 0 og 1' % (r,))
    felles = o.get('felles_chip') or {}
    if set(felles) - {'BB', 'FH'}:
        feil.append('felles_chip kan bare ha BB og FH')
    bb, fh = felles.get('BB'), felles.get('FH')
    if bb is not None and 'BB' in chips and bb not in chips['BB']:
        feil.append('felles_chip BB %s er ikke blant chips BB %s' % (bb, chips['BB']))
    if fh is not None and 'FH' in chips and fh not in chips['FH']:
        feil.append('felles_chip FH %s er ikke blant chips FH %s' % (fh, chips['FH']))
    if bb is not None and bb == fh:
        feil.append('Bench Boost og Free Hit kan ikke stå i samme runde (%s)' % bb)
    if uke_mappe is not None and o.get('overstyringer') and not (Path(uke_mappe) / o['overstyringer']).exists():
        feil.append('overstyringsfilen %s finnes ikke' % o['overstyringer'])
    if feil:
        raise ValueError('Feil i oppsett.json: ' + '; '.join(feil))


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def tall(o):
    """json-hjelper for numpy-typer."""
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


def kjor(uke_mappe, ut=None, bare_poeng=False, uten_skadesim=False, oppsett=None, logg=print):
    """Hele ukekjøringen. Returnerer dict med resultatene (samme som skrives til fil)."""
    start = time.time()
    uke_mappe = Path(uke_mappe).resolve()
    ut = Path(ut).resolve() if ut else uke_mappe / 'motor'
    ut.mkdir(parents=True, exist_ok=True)
    o = oppsett or les_json(uke_mappe / 'motor' / 'oppsett.json')
    kontroller_oppsett(o, uke_mappe)
    runde = int(o['runde'])
    slutt = int(o.get('horisont_til') or min(runde + 9, 19 if runde <= 19 else 38))
    bank = None if o.get('bank') is None else round(10 * float(o['bank']))
    inn = uke_mappe / o.get('input_mappe', 'motor/input')
    u = Uke.fra_mappe(uke_mappe, runde, slutt, bank=bank, sesong=o.get('sesong'), input_mappe=inn)
    u.kontroller_input()
    u.kontroller_tropp()

    # 1. Minutter og spillerpoeng
    tabell = o.get('minuttabell')
    over = o.get('overstyringer', 'claude/minutter_overstyring.csv')
    over = uke_mappe / over if over and (uke_mappe / over).exists() else None
    md, retur = poeng.lag_minutter(u, overstyringer=over, minuttabell=uke_mappe / tabell if tabell else None)
    pr = poeng.prognose(u, md, retur)
    poeng.skriv_minutter(u, md, ut / 'minutter.csv', retur)
    vekt = float(o.get('vekt_codex', .5))
    g0 = u.g0
    skriv_csv(ut / 'spillerpoeng.csv', [dict(
        id=p, navn=u.E[p]['web_name'], lag=u.T[u.E[p]['team']], pos=KINDS[u.E[p]['element_type']],
        pris=u.E[p]['now_cost'] / 10, gw=g, kamper=len(u.kamper.get((g, u.E[p]['team']), [])), p_start=md[p, g][0],
        forventede_min=md[p, g][1], p_spiller=round(pr.PP[u.ix[p], g - g0], 6),
        codex=round(pr.XP[u.ix[p], g - g0], 6), repo_hybrid=round(pr.REPO[u.ix[p], g - g0], 6),
        blend=round(vekt * pr.XP[u.ix[p], g - g0] + (1 - vekt) * pr.REPO[u.ix[p], g - g0], 6))
        for p in u.ids for g in u.GWS])
    skriv_csv(ut / 'lagstyrke.csv', [dict(lag=u.T[t], xG=v[0], xGA=v[1], kamper=v[2], angrep=pr.strength[t][0],
                                          forsvar=pr.strength[t][1]) for t, v in sorted(pr.tm.items())])
    doble = sorted({g for (g, t), k in u.kamper.items() if g in u.GWS and len(k) > 1})
    blanke = sorted({g for g in u.GWS for t in u.T if not u.kamper.get((g, t))})
    kontroll = dict(runde=runde, horisont_til=slutt, spillere=u.N, bank=u.bank / 10, budsjett=u.budsjett / 10,
                    gratisbytter=o['gratisbytter'], vekt_codex=vekt, repo_runder=pr.repo_runder,
                    repo_rader_uten_bruk=pr.repo_mangler, kjopsunivers=len(pr.UI), ute=len(pr.blocked),
                    overstyringsfil=str(over) if over else None, minuttabell=tabell, retur_fra_fravaer=len(retur),
                    dobbeltrunder=doble, blanke_runder=blanke,
                    inndata_sha256={fn: sha(inn / fn) for fn in FRYSES})
    logg('Spillerpoeng ferdig: %d spillere, runde %d-%d. Doble: %s. Blanke: %s.' % (u.N, runde, slutt, doble, blanke))
    if bare_poeng:
        kontroll['status'] = 'OK (bare poeng)'
        skriv_json(ut / 'kontroll.json', kontroll)
        return dict(uke=u, prognose=pr, kontroll=kontroll)

    # 2. Standardanalyse: søk, rutenett, A-D, E, F, G
    chips = o.get('chips', {})
    m = Motor(u, pr, ft=o['gratisbytter'], vekt=vekt, bb_runder=chips.get('BB'), fh_runder=chips.get('FH'),
              fh_start=o.get('fh_start'), tmp=ut)
    res = m.standardanalyse(maks_bytter=int(o.get('maks_bytter', 4)), logg=logg)
    skriv_csv(ut / 'alternativer.csv', res['alternativer'])
    skriv_csv(ut / 'byttesok.csv', res['byttesok'])
    skriv_csv(ut / 'chiprutenett.csv', res['rutenett'])
    skriv_csv(ut / 'kapteiner.csv', res['kapteiner'])
    logg('Standardanalyse ferdig etter %.0f s: valg %s, BB %s, FH %s' % (time.time() - start, res['valg'], res['bb'], res['fh']))

    # 3. Felles chipdatoer: rull, søkets beste og Claudes egne alternativer på nøyaktig samme vilkår
    felles = o.get('felles_chip') or {}
    bb = felles.get('BB', res['bb'])
    fh = felles.get('FH', res['fh'])
    tropper = {m.etikett(n): s for n, s in res['valgt'].items()}
    for a in o.get('alternativer', []):
        assert a['navn'] not in tropper, 'Alternativnavn i bruk: ' + a['navn']
        tropper[a['navn']] = m.tropp_etter(a.get('ut', []), a.get('inn', []))
    planer, rader = m.faste_planer(tropper, bb, fh)
    skriv_csv(ut / 'alternativer_felles.csv', rader)
    egne = [a['navn'] for a in o.get('alternativer', [])]
    if egne:      # hvert eget alternativ med alle lovlige chipdatoer, ikke bare de felles (Codex' kontroll, F11)
        skriv_csv(ut / 'chiprutenett_egne.csv', m.rutenett_for({k: tropper[k] for k in egne}))
    if o.get('ft_folsomhet'):
        skriv_csv(ut / 'ft_folsomhet.csv', m.ft_folsomhet(tropper, bb, fh, o['ft_folsomhet']))
    (ut / 'planer.json').write_text(__import__('json').dumps(
        dict(valg=res['valg'], BB=res['bb'], FH=res['fh'], hoved=res['planer'], FH_planer=res['fh_planer'],
             kollisjon=res['kollisjon'], felles=dict(BB=bb, FH=fh, planer=planer)),
        ensure_ascii=False, indent=1, default=tall))
    avvik = max(m.kontroller_bane(p) for p in list(res['planer'].values()) + list(planer.values()))
    assert avvik < 1e-6, 'Planene kan ikke regnes på nytt fra spillerpoeng og vekter'
    kontroll.update(valg=res['valg'], BB=res['bb'], FH=res['fh'], felles_BB=bb, felles_FH=fh,
                    alternativer=list(tropper), maks_avvik_gjenregning=avvik)

    # 4. Paret skadesimulering på de samme troppene og chipdatoene. Uten tilgjengelig Bench Boost sammenlignes totalene
    #    uten BB; før 21. nov ble simuleringen da hoppet over uten melding (Codex' kontroll, F6).
    ss = o.get('skadesim', {})
    n_trekk = int(ss.get('trekk', 200))
    if uten_skadesim or n_trekk == 0:
        kontroll['skadesim'] = 'ikke kjørt (%s)' % ('--uten-skadesim' if uten_skadesim else 'trekk: 0 i oppsettet')
        logg('Skadesimuleringen er ikke kjørt: ' + kontroll['skadesim'])
    else:
        trekk, sim, par = skadesim.simuler(m, tropper, bb, fh, rater=tuple(ss.get('rater', [.01, .02])),
                                           trekk=n_trekk, fro=int(ss.get('fro', 7089878)), logg=logg)
        skriv_csv(ut / 'skadetrekk.csv', trekk)
        skriv_csv(ut / 'skadesim.csv', sim)
        skriv_csv(ut / 'parvise.csv', par)
        kontroll['skadesim'] = dict(trekk=n_trekk, rater=ss.get('rater', [.01, .02]), BB=bb, FH=fh)
    for f in ut.glob('*-pulp.*'):           # rester etter heltallsløseren
        f.unlink()
    kontroll.update(status='OK', sekunder=round(time.time() - start, 1))
    skriv_json(ut / 'kontroll.json', kontroll)
    logg('FERDIG etter %.0f s. Filer i %s' % (time.time() - start, ut))
    return dict(uke=u, prognose=pr, motor=m, standard=res, planer=planer, felles=rader, kontroll=kontroll)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('uke', help='ukemappe, f.eks. samarbeid/gw11')
    ap.add_argument('--frys', action='store_true', help='kopier data/derived-filene til gwNN/motor/input/ og avslutt')
    ap.add_argument('--bare-poeng', action='store_true', help='bare minutter og spillerpoeng (sekunder)')
    ap.add_argument('--uten-skadesim', action='store_true', help='hopp over skadesimuleringen (sparer flere minutter)')
    ap.add_argument('--ut', help='utmappe (standard: gwNN/motor)')
    a = ap.parse_args()
    if a.frys:
        return frys(Path(a.uke).resolve())
    try:
        kjor(a.uke, ut=a.ut, bare_poeng=a.bare_poeng, uten_skadesim=a.uten_skadesim)
    except ValueError as e:
        raise SystemExit(str(e))


if __name__ == '__main__':
    main()
