"""
Evalueringsrigg for PREDIKSJON — måler om en endring gjør modellen mer treffsikker.

HVORFOR DENNE FINNES VED SIDEN AV evaluate.py

Det finnes to slags endringer, og de trenger hvert sitt måleinstrument.

    Prediksjonsendringer   hvordan xP regnes ut: krymping, priorer, skalering
                           etter motstander, lagstyrke.
    Beslutningsendringer   hva laget gjør med xP: byttegrense, kostnad for hit,
                           benkvekt, hvor mange runder fram man planlegger.

En beslutningsendring kan bare måles ved å spille en hel sesong, for verdien
ligger i stien: ett bytte i runde 4 gir et annet lag i runde 20. Det er
evaluate.py. Prisen er at standardfeilen er 6-15 poeng selv med parvise
kjøringer, og en full test tar timevis.

En prediksjonsendring trenger ikke det. Den kan måles direkte på hver enkelt
prediksjon, og der er datagrunnlaget 24 000 rader per sesong i stedet for én
sesongtotal. Standardfeilen på MAE blir 0,0004 — over tusen ganger skarpere.

    Sesongsimulering   én sesongtotal per kjøring    standardfeil ~6 poeng
    Parvis backtest    24 577 prediksjoner            standardfeil 0,0004 MAE

Konsekvensen er en regel: en endring i prediksjonsmodellen måles HER først.
Sesongsimuleringen brukes bare når spørsmålet faktisk handler om beslutninger,
eller til slutt for å bekrefte at en målt forbedring i xP også blir til poeng.

HVORFOR PARVIS

Begge konfigurasjonene predikerer nøyaktig de samme radene fra nøyaktig de
samme treningsdataene. Forskjellen tas rad for rad. Da forsvinner all den
felles variasjonen — at Haaland scoret hat trick i runde 12 rammer begge like
hardt — og bare effekten av endringen står igjen.

HVA SOM MÅLES

    MAE          gjennomsnittlig absoluttfeil. Parvis differanse med
                 standardfeil, så det går an å si om forskjellen er reell.
    Spearman     rangeringsevne blant dem som faktisk spilte. To tredjedeler
                 av radene er spillere som ikke spilte; de rangeres perfekt av
                 hva som helst og drukner signalet.
    topp k       hva de k høyest rangerte faktisk scoret. Dette er det som
                 ligner mest på å velge lag, og derfor det som betyr mest.

BRUK

    from evaluate_pred import compare
    compare({"uten": lambda: setattr(B, "ATT_SCALING", False),
             "med":  lambda: setattr(B, "ATT_SCALING", True)})

Hver konfigurasjon er en funksjon som setter det den vil endre og returnerer
en funksjon som setter det tilbake (eller None, hvis den rydder selv).
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))
import backtest as B

BASE = ("https://raw.githubusercontent.com/vaastav/"
        "Fantasy-Premier-League/master/data")
# Tre sesonger. Hver ekstra sesong strammer standardfeilen og — viktigere —
# verner mot funn som bare gjelder ett bestemt år. Byttegrensen er det stående
# eksempelet: den så ut som et sikkert funn på over tretti standardfeil i
# 2024-25 og pekte motsatt vei i 2025-26.
#
# 2022-23 er den eldste som kan brukes som testsesong, og 2021-22 den eldste i
# det hele tatt: der mangler kildene expected_goals, expected_assists og starts,
# og uten dem finnes verken angrepsmodellen eller minuttmodellen.
SEASONS = ("2025-26", "2024-25", "2023-24")
# Forrige sesong per sesong. Brukes til den personlige spilletidsprioren, som
# er den største enkeltgevinsten som er målt i dette prosjektet. Uten den måler
# backtesten en minuttmodell som ikke er den produksjonen kjører.
PRIOR_OF = {"2025-26": "2024-25", "2024-25": "2023-24", "2023-24": "2022-23"}

_cache: dict[str, pd.DataFrame] = {}
_sprior: dict[str, pd.DataFrame] = {}


def load_season(season: str) -> pd.DataFrame:
    """Rader med motstander påført. Hentes én gang og gjenbrukes."""
    if season in _cache:
        return _cache[season]
    old, B.HIST = B.HIST, f"{BASE}/{season}"
    try:
        d = B.load()
    finally:
        B.HIST = old
    sides = d.groupby(["fixture", "team"], as_index=False).size()
    opp = sides.merge(sides, on="fixture")
    opp = opp[opp.team_x != opp.team_y][["fixture", "team_x", "team_y"]]
    opp = opp.rename(columns={"team_x": "team", "team_y": "_opp_name"}).drop_duplicates()
    _cache[season] = d.merge(opp, on=["fixture", "team"], how="left")
    return _cache[season]


def start_prior_for(season: str) -> pd.DataFrame | None:
    """Personlig startrate fra sesongen før. None hvis den ikke finnes."""
    prev = PRIOR_OF.get(season)
    if prev is None:
        return None
    if prev not in _sprior:
        old, B.HIST = B.HIST, f"{BASE}/{prev}"
        try:
            _sprior[prev] = B.start_prior(B.load())
        except Exception as e:                    # sesongen finnes ikke i kilden
            print(f"  (ingen prior for {season}: {e})")
            _sprior[prev] = None
        finally:
            B.HIST = old
    return _sprior[prev]


def walk_forward(d: pd.DataFrame, sprior: pd.DataFrame | None = None,
                 prev: pd.DataFrame | None = None, first_gw: int | None = None) -> pd.DataFrame:
    """
    Én full gjennomkjøring med gjeldende innstillinger i backtest.

    Med `prev` — forrige sesongs kamper — kan testen starte tidlig i sesongen i
    stedet for i runde 8. Det er ikke en detalj: runde 2 til 7 er der modellen
    vet minst og der prioren gjør hele jobben, og det er nøyaktig der vi
    befinner oss når sesongen er i gang. En evaluering som hopper over dem
    måler ikke den delen av året som er vanskeligst.

    Forrige sesong legges inn i treningsgrunnlaget de første rundene, slik
    sesongsimuleringen gjør, og lagratingene krympes mot fjorårets. Uten det
    ville de første rundene krympe mot «alle lag er like gode».
    """
    team_prior = None
    if prev is not None and not prev.empty:
        pa, pdf, _, _ = B.team_ratings(prev)
        team_prior = (pa, pdf)
    start = first_gw if first_gw is not None else B.FIRST_TEST_GW

    acc = []
    for t in sorted(g for g in d.GW.unique() if g >= start):
        hist, test = d[d.GW < t], d[d.GW == t]
        if test.empty:
            continue
        # De første rundene har for lite data til å stå alene.
        if prev is not None and len(hist) < 6 * 380:
            train = pd.concat([prev, hist], ignore_index=True)
        else:
            train = hist
        if train.empty:
            continue
        att, dfn, ha, mu = B.team_ratings(train, team_prior)
        if not att:
            continue
        # En spiller som byttet posisjon mellom sesongene får to rader når
        # forrige og inneværende slås sammen. Behold raden med mest spilletid,
        # ellers gir oppslaget en tabell i stedet for én spiller.
        rates = B.per90(train, sprior).sort_values("mins", ascending=False)
        rates = rates.drop_duplicates("name")
        preds = B.predict(test, rates, att, dfn, ha, mu, B.fit_dispersion(train))
        if preds.empty:
            continue
        # Baselinene skal bare se inneværende sesong — «form» betyr de tre
        # siste rundene, ikke tre runder for fjorten måneder siden.
        recent = hist[hist.GW >= t - 3].groupby("name").total_points.mean()
        season_avg = hist.groupby("name").total_points.mean()
        preds["b_form"] = preds.name.map(recent).fillna(preds.name.map(season_avg)).fillna(0)
        acc.append(preds)
    return pd.concat(acc, ignore_index=True)


def compare(configs: dict, seasons=SEASONS, use_prior=True,
            first_gw: int | None = None) -> pd.DataFrame:
    """
    Kjører hver konfigurasjon på hver sesong og skriver en parvis sammenligning.

    Den første konfigurasjonen er grunnlinjen; alle andre måles mot den.
    `first_gw` lavere enn 8 krever forrige sesong, som følger med use_prior.
    """
    names = list(configs)
    runs: dict[tuple[str, str], pd.DataFrame] = {}
    for season in seasons:
        d = load_season(season)
        sprior = start_prior_for(season) if use_prior else None
        prev = load_season(PRIOR_OF[season]) if (use_prior and season in PRIOR_OF) else None
        for nm in names:
            undo = configs[nm]()
            try:
                runs[(season, nm)] = walk_forward(d, sprior, prev, first_gw)
            finally:
                if callable(undo):
                    undo()
            print(f"  kjørt {season} / {nm}: {len(runs[(season, nm)])} prediksjoner",
                  flush=True)

    # Kjøringene går gjennom nøyaktig de samme radene i samme rekkefølge, så de
    # er allerede stilt opp mot hverandre. Det verifiseres i stedet for å
    # antas — en sammenslåing på navn ville dessuten sprekke på spillere som
    # deler navn og på doble runder, der samme nøkkel finnes to ganger.
    key = ["name", "gw", "fixture"]
    out = []
    for season in seasons:
        base = runs[(season, names[0])]
        merged = base[key + ["actual", "mins", "b_form"]].copy()
        for nm in names:
            other = runs[(season, nm)]
            if len(other) != len(base) or not other[key].equals(base[key]):
                raise RuntimeError(
                    f"{season}/{nm} ga andre rader enn {names[0]} — "
                    "da er ikke sammenligningen parvis lenger")
            merged[f"xp__{nm}"] = other.xp.to_numpy()
        merged["season"] = season
        out.append(merged)
    p = pd.concat(out, ignore_index=True)
    _report(p, names)
    return p


def _report(p: pd.DataFrame, names: list[str]) -> None:
    played = p[p.mins > 0]
    print(f"\n  {len(p)} prediksjoner ({len(played)} spilte) over "
          f"{p.season.nunique()} sesong(er)\n")
    print(f"  {'konfig':16s} {'MAE':>8s} {'RMSE':>8s} {'Spearman':>10s} {'topp10':>8s} {'topp20':>8s}")
    for nm in names:
        c = f"xp__{nm}"
        mae = (p[c] - p.actual).abs().mean()
        rmse = np.sqrt(((p[c] - p.actual) ** 2).mean())
        rho = spearmanr(played[c], played.actual).statistic
        tops = [p.groupby(["season", "gw"], group_keys=False)
                .apply(lambda g: g.nlargest(k, c), include_groups=False).actual.mean()
                for k in (10, 20)]
        print(f"  {nm:16s} {mae:8.4f} {rmse:8.4f} {rho:10.4f} "
              f"{tops[0]:8.2f} {tops[1]:8.2f}")

    if len(names) < 2:
        return
    a = names[0]
    print(f"\n  PARVIS MAE, rad for rad, alt målt mot «{a}»")
    print("  (negativ differanse = mindre feil = bedre)")
    for b in names[1:]:
        print(f"\n    {b}")
        for season in list(p.season.unique()) + (["alle"] if p.season.nunique() > 1 else []):
            q = p if season == "alle" else p[p.season == season]
            d_ae = (q[f"xp__{b}"] - q.actual).abs() - (q[f"xp__{a}"] - q.actual).abs()
            se = d_ae.std(ddof=1) / np.sqrt(len(d_ae))
            sig = abs(d_ae.mean()) / se if se else 0.0
            mark = "BEDRE" if d_ae.mean() < 0 and sig > 2 else (
                "DÅRLIGERE" if d_ae.mean() > 0 and sig > 2 else "ikke etablert")
            print(f"      {season:9s} {d_ae.mean():+.5f} ± {se:.5f} "
                  f"({sig:4.1f} se)  → {mark}")

    # Tidlig mot sent i sesongen. En prior er per definisjon viktigst når det
    # finnes lite annet å bygge på. Måles bare runde 8 og utover, er spørsmålet
    # om priorvekt allerede avgjort før man begynner å måle — modellen har da
    # sju runder egne data og prioren kan nesten bare skade. Snittet over hele
    # sesongen skjuler dette, for de tidlige rundene er få.
    if (p.gw < 8).any() and (p.gw >= 8).any():
        print(f"\n  TIDLIG MOT SENT, parvis MAE mot «{a}»")
        for b in names[1:]:
            cells = []
            for lab, q in (("runde 2-7", p[p.gw < 8]), ("runde 8+", p[p.gw >= 8])):
                d_ae = (q[f"xp__{b}"] - q.actual).abs() - (q[f"xp__{a}"] - q.actual).abs()
                se = d_ae.std(ddof=1) / np.sqrt(len(d_ae))
                cells.append(f"{lab} {d_ae.mean():+.5f} ({abs(d_ae.mean())/se if se else 0:4.1f} se)")
            print(f"    {b:16s} " + " | ".join(cells))

    # MAE er ikke det FPL betaler for. Det som betyr noe er om de spillerne
    # modellen rangerer øverst faktisk leverer. Her tas differansen per runde,
    # slik at hver runde er ett par — det gir en standardfeil på et mål som
    # ellers bare oppgis som et nakent snitt.
    print(f"\n  PARVIS TOPP-K, differanse per runde, målt mot «{a}»")
    print("  (positiv differanse = de utvalgte scoret mer = bedre)")
    for k in (10, 20, 50):
        line = []
        for b in names[1:]:
            per_gw = []
            for _, g in p.groupby(["season", "gw"]):
                per_gw.append(g.nlargest(k, f"xp__{b}").actual.mean()
                              - g.nlargest(k, f"xp__{a}").actual.mean())
            v = np.array(per_gw, float)
            se = v.std(ddof=1) / np.sqrt(len(v))
            line.append(f"{b}: {v.mean():+.3f} ± {se:.3f} ({abs(v.mean())/se if se else 0:.1f} se)")
        print(f"    topp {k:2d}  " + " | ".join(line))


if __name__ == "__main__":
    compare({"uten skala": lambda: (setattr(B, "ATT_SCALING", False), None)[1],
             "med skala": lambda: (setattr(B, "ATT_SCALING", True), None)[1]})
