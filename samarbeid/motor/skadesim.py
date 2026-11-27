"""Paret skadesimulering: de samme tilfeldige fraværene rammer alle alternativer og begge poengsett.

Flyttet fra samarbeid/gw10/codex/modell.py linje 577-594 og modell_r2.py linje 83-106.

Modell (stressantakelse, ikke estimert skaderate): fra og med ANDRE runde i horisonten får hver spiller som ikke
allerede er ute, et nytt fravær med sannsynlighet `rate` per runde. Varighet 1, 2, 3 eller 6 runder, like sannsynlig.
Byttepolitikken kjenner bare fravær som har inntruffet; framtidige er skjult. Fravær rammer også kjøpskandidater.
Kampflaks og modellfeil er IKKE med: spredningen her er spredning i forventede poeng mellom skadeverdener.
"""
import numpy as np

BLOKK = 100     # verdener trekkes i blokker på 100, så tidligere verdener gjenskapes når flere legges til


def trekk_verdener(N, H, trekk, fro):
    """Returnerer (U, varighet) med form (trekk, H, N). Samme frø gir samme første verdener uansett `trekk`."""
    rng = np.random.default_rng(fro)
    UU, DD = [], []
    for _ in range((trekk + BLOKK - 1) // BLOKK):
        UU.append(rng.random((BLOKK, H, N)))
        DD.append(np.array([1, 2, 3, 6], dtype=np.int16)[rng.integers(0, 4, size=(BLOKK, H, N))])
    return np.concatenate(UU)[:trekk], np.concatenate(DD)[:trekk]


def verden(U, varighet, rate):
    """world[t, i] = første kolonne spiller i igjen er tilgjengelig, sett fra runde t (0 = tilgjengelig)."""
    H, N = U.shape
    world = np.zeros((H, N), dtype=np.int16)
    end = np.zeros(N, dtype=np.int16)
    for t in range(1, H):
        new = (end <= t) & (U[t] < rate)
        end[new] = t + varighet[t, new]
        world[t] = end
    return world


def simuler_raa(motor, tropper, fh, rate, trekk, fro, logg=None):
    """Kjør alle tropper gjennom de samme verdenene.

    Returnerer {navn: array (trekk, H + 1, 2)}: rad t < H er totalen med Bench Boost i runde g0 + t (`alle_BB`),
    og siste rad (indeks H) er totalen uten Bench Boost.
    """
    U, D = trekk_verdener(motor.N, motor.H, trekk, fro)
    motor.lag_maler()
    ut = {k: [] for k in tropper}
    for d in range(trekk):
        w = verden(U[d], D[d], rate)
        for k, s in tropper.items():
            p = motor.bane(s, fh=fh, world=w, record=False)
            ut[k].append(p['alle_BB'] + [p['total_uten_BB']])
        if logg and (d + 1) % 20 == 0:
            logg('Skadesim rate %.2f: %d / %d' % (rate, d + 1, trekk))
    return {k: np.array(v) for k, v in ut.items()}


def simuler(motor, tropper, bb, fh, rater=(.01, .02), trekk=200, fro=7089878, referanse=None, logg=None):
    """Paret simulering med felles BB- og FH-runde. Returnerer (trekkrader, nivårader, parvise rader).

    bb: Bench Boost-runden, eller None når BB ikke er tilgjengelig (da sammenlignes totalene uten BB; før 21. nov
        ble simuleringen da hoppet over uten melding, Codex' kontroll F6).
    referanse: navnet på alternativet de andre sammenlignes mot (standard: det første, normalt «A» = rull).
    """
    navn = list(tropper)
    referanse = referanse or navn[0]
    col = motor.H if bb is None else bb - motor.g0
    sett = ['codex', 'repo_hybrid', 'blend']
    trials, sim, par = [], [], []
    for rate in rater:
        raa = simuler_raa(motor, tropper, fh, rate, trekk, fro, logg)
        res = {}
        for k in navn:
            v = raa[k][:, col, :]
            res[k] = np.column_stack([v[:, 0], v[:, 1], motor.bland([v[:, 0], v[:, 1]])])
            for d in range(trekk):
                trials.append(dict(p=rate, verden=d, alternativ=k, BB=bb if bb is not None else '',
                                   FH=fh if fh is not None else '', codex=res[k][d, 0],
                                   repo_hybrid=res[k][d, 1], blend=res[k][d, 2]))
        ref = res[referanse]
        for k in navn:
            a = res[k]
            delta = a - ref
            for m, s in enumerate(sett):
                sim.append(dict(p=rate, alternativ=k, poengsett=s, snitt=a[:, m].mean(), p10=np.quantile(a[:, m], .1),
                                p90=np.quantile(a[:, m], .9), snitt_SE=a[:, m].std(ddof=1) / np.sqrt(trekk), n=trekk))
                par.append(dict(p=rate, alternativ=k, referanse=referanse, poengsett=s, delta_snitt=delta[:, m].mean(),
                                andel_vinner=(delta[:, m] > 1e-9).mean(), p10=np.quantile(delta[:, m], .1),
                                p90=np.quantile(delta[:, m], .9), paret_SE=delta[:, m].std(ddof=1) / np.sqrt(trekk), n=trekk))
    return trials, sim, par
