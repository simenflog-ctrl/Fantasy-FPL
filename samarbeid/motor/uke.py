"""Ukens inndata samlet i ett objekt. Ingen beregning her, bare innlesing.

Flyttet fra samarbeid/gw10/codex/modell.py (linje 22-30 og 121-125). Forskjellen er at
runde, horisont, bank og sesong er parametre i stedet for tall skrevet inn i koden.
"""
import csv
import json
from pathlib import Path

import numpy as np

KINDS = {1: 'GKP', 2: 'DEF', 3: 'MID', 4: 'FWD'}
COUNTS = {1: 2, 2: 5, 3: 5, 4: 3}


def les_json(p):
    return json.loads(Path(p).read_text())


def les_csv(p):
    with Path(p).open() as f:
        return list(csv.DictReader(f))


def skriv_csv(p, rader):
    assert rader, 'Ingen rader til ' + str(p)
    with Path(p).open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=list(rader[0]))
        w.writeheader()
        w.writerows(rader)


def skriv_json(p, obj):
    Path(p).write_text(json.dumps(obj, ensure_ascii=False, indent=2))


def heltall(v):
    """v som int når v er et helt tall (også 2.0, "2" og numpy-heltall), ellers None. bool godtas ikke.

    Brukes til å avvise 1,9 gratisbytter og lignende i stedet for å runde dem stille av til et lovlig tall.
    """
    if isinstance(v, bool):
        return None
    try:
        f = float(v)
    except (TypeError, ValueError):
        return None
    return int(f) if f.is_integer() else None


def vindu_slutt(runde):
    """Siste runde i chipvinduet runden ligger i: 19 i første halvdel, 38 i andre."""
    return 19 if int(runde) <= 19 else 38


class Uke:
    """Frosne data for én beslutningsrunde.

    bootstrap  : bootstrap-static (elements, teams, game_config.scoring)
    fixtures   : fixtures-listen for hele sesongen
    salg       : liste av {'id', 'salgspris'} for de 15 i troppen (salgspris i millioner)
    history    : {spiller-id: element-summary} med 'history' og 'history_past'
    pm         : rader fra repoets player_matches.csv (element, fixture, team, gw, minutes, expected_goals)
    repo       : rader fra repoets expected_points.csv (element, gw, xp, exp_minutes)
    runde      : første runde i horisonten (runden det skal tas beslutning for)
    slutt      : siste runde i horisonten
    bank       : penger i banken, i tideler av en million (0,4 mill = 4)
    sesong     : f.eks. '2026/27'; rader i history_past fra denne sesongen eller senere brukes ikke
    """

    def __init__(self, bootstrap, fixtures, salg, history, pm, repo, runde, slutt, bank, sesong):
        self.b = bootstrap
        self.E = {e['id']: e for e in bootstrap['elements']}
        self.ids = sorted(self.E)
        self.ix = {p: i for i, p in enumerate(self.ids)}
        self.N = len(self.ids)
        self.T = {t['id']: t['short_name'] for t in bootstrap['teams']}
        self.sc = bootstrap['game_config']['scoring']
        self.fx = fixtures
        self.history = history
        self.g0 = int(runde)
        self.siste = self.g0 - 1          # siste spilte runde
        self.slutt = int(slutt)
        self.GWS = list(range(self.g0, self.slutt + 1))
        self.H = len(self.GWS)
        self.sesong = sesong
        self.pm = [r for r in pm if int(r['gw']) <= self.siste]
        self.repo = repo
        self.bank = int(bank)
        ids, E, ix = self.ids, self.E, self.ix
        self.POS = np.array([E[p]['element_type'] for p in ids])
        self.TEAM = np.array([E[p]['team'] for p in ids])
        self.COST = np.array([E[p]['now_cost'] for p in ids])
        self.SALES = self.COST.copy()
        osell = {r['id']: round(10 * r['salgspris']) for r in salg}
        for p, v in osell.items():
            self.SALES[ix[p]] = v
        self.orig = frozenset(osell)
        self.ORIG = np.array(sorted([ix[p] for p in self.orig], key=lambda i: (self.POS[i], i)), dtype=np.int64)
        self.budsjett = sum(osell.values()) + self.bank   # salgsverdi + bank, tideler
        # Kampene per (runde, lag), i samme rekkefølge som fixtures-listen.
        self.kamper = {}
        for f in fixtures:
            if not f['event']:
                continue
            self.kamper.setdefault((f['event'], f['team_h']), []).append(f)
            self.kamper.setdefault((f['event'], f['team_a']), []).append(f)

    @classmethod
    def fra_mappe(cls, mappe, runde, slutt, bank=None, sesong=None, input_mappe=None):
        """Les en ukemappe (samarbeid/gwNN). input_mappe har de frosne repo-filene."""
        mappe = Path(mappe)
        D = mappe / 'data'
        IN = Path(input_mappe) if input_mappe else mappe / 'motor' / 'input'
        fixtures = les_json(D / 'fixtures.json')
        history = {int(p.stem): les_json(p) for p in (D / 'element_summary').glob('*.json')}
        if not history:
            raise FileNotFoundError('Mangler ' + str(D / 'element_summary') + ' (ligger ikke i git; hent eller kopier)')
        if bank is None:
            bank = les_json(D / 'entry.json')['last_deadline_bank']
        if sesong is None:
            sesong = sesongnavn(fixtures)
        return cls(les_json(D / 'bootstrap.json'), fixtures, les_json(D / 'salgspriser.json'), history,
                   les_csv(IN / 'player_matches.csv'), les_csv(IN / 'expected_points.csv'),
                   runde, slutt, bank, sesong)

    def navn(self, indekser):
        """Kommaseparerte web_name for en liste av interne indekser."""
        return ', '.join(self.E[self.ids[int(i)]]['web_name'] for i in indekser)

    def finn(self, ref, blant=None):
        """Intern indeks for en spiller gitt som ID (int eller tallstreng) eller entydig web_name.

        blant: interne indekser navnet skal letes blant (f.eks. dagens tropp når det gjelder salg).
        """
        if isinstance(ref, (int, np.integer)) or str(ref).isdigit():
            return self.ix[int(ref)]
        utvalg = self.ids if blant is None else [self.ids[int(i)] for i in blant]
        treff = [p for p in utvalg if self.E[p]['web_name'] == ref]
        if len(treff) != 1:
            raise ValueError('Spillernavn %r gir %d treff; bruk ID' % (ref, len(treff)))
        return self.ix[treff[0]]

    def kontroller_input(self):
        """Den frosne player_matches-filen må stemme med bootstrap (samme kontroll som gw10, linje 35)."""
        agg = {}
        for r in self.pm:
            a = agg.setdefault(int(r['element']), [0., 0.])
            a[0] += float(r['minutes'])
            a[1] += float(r['expected_goals'])
        feil = [p for p, e in self.E.items()
                if agg.get(p, [0., 0.])[0] != e['minutes'] or abs(agg.get(p, [0., 0.])[1] - float(e['expected_goals'])) >= .05]
        if feil:
            raise ValueError('player_matches.csv stemmer ikke med bootstrap for %d spillere, f.eks. id %s' % (len(feil), feil[:5]))

    def kontroller_tropp(self):
        s = self.ORIG
        assert len(s) == 15, 'salgspriser.json må ha 15 spillere'
        assert [int(sum(self.POS[s] == k)) for k in range(1, 5)] == [2, 5, 5, 3], 'troppen er ikke 2/5/5/3'


def sesongnavn(fixtures):
    """'2026/27' ut fra første avspark i kampprogrammet."""
    y = int(min(f['kickoff_time'] for f in fixtures if f.get('kickoff_time'))[:4])
    return '%d/%02d' % (y, (y + 1) % 100)
