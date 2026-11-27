#!/usr/bin/env python3
"""Steg 4: små grenseeksempler for CLI og Motor. Faste mapper under motorkontroll-data/."""
import json
import subprocess
import sys
import time
import motorkontroll_eksempler as a

start = time.monotonic()
resultat = []
def logg(test, dom='OK', **kw):
    row = dict(test=test, dom=dom, **kw)
    resultat.append(row)
    print(json.dumps(row, ensure_ascii=False), flush=True)
    (a.UT / 'chips.json').write_text(json.dumps(resultat, ensure_ascii=False, indent=2))

def stopp(navn, fn):
    try:
        fn()
    except (ValueError, AssertionError, TypeError) as e:
        assert str(e), 'Tom feilmelding'
        logg(navn, melding=type(e).__name__ + ': ' + str(e))
    else:
        logg(navn, 'GJENSTÅR', melding='Ingen avvisning')

u, md, pr = a.liga()
w = a.skriv_uke(u, 'chips-uke')
o = dict(runde=6, horisont_til=9, gratisbytter=2, maks_bytter=0,
         chips={'BB': [], 'FH': []}, skadesim={'trekk': 0})
r = a.kj(w, o)
assert r['standard']['bb'] is None and r['standard']['fh'] is None
assert all(x['BB'] == x['FH'] == '' for x in r['standard']['rutenett'])
assert all(x['BB'] == x['FH'] == '' for x in r['felles'])
logg('Tomme BB/FH-lister: CLI og Motor full analyse', rutenett=r['standard']['rutenett'])

# Virkelig CLI-prosess, inkludert --bare-poeng som skal stoppe før prognosen.
for endring in [dict(chips={'WC': [6]}), dict(chips={'TC': [6]}), dict(chips={'FH': [6]}),
                dict(felles_chip={'WC': 6}), dict(felles_chip={'TC': 6})]:
    a.skriv_json(w / 'motor/oppsett.json', dict(o, **endring))
    proc = subprocess.run([sys.executable, str(a.MOTOR / 'kjor.py'), str(w), '--bare-poeng'], capture_output=True, text=True)
    assert proc.returncode != 0 and proc.stderr.strip()
    logg('CLI stopper før spillerpoeng', oppsett=endring, melding=proc.stderr.strip())

m = a.Motor(u, pr, bb_runder=[7, 8], fh_runder=[7, 8])
# F7 (23. nov): direkte Motor avviser oppgitte BB/FH-runder utenfor horisonten i stedet for å filtrere dem.
try:
    outside = a.Motor(u, pr, bb_runder=[20], fh_runder=[])
except (ValueError, AssertionError) as e:
    logg('F7: Motor avviser BB-runde utenfor horisonten', 'RETTET', melding=str(e))
else:
    logg('F7: Motor avviser BB-runde utenfor horisonten', 'GJENSTÅR',
         gitt=[20], faktisk=outside.bb_runder)
try:
    a.Motor(u, pr, bb_runder=[], fh_runder=[10])
except (ValueError, AssertionError) as e:
    logg('F7: Motor avviser FH-runde utenfor horisonten', 'RETTET', melding=str(e))
else:
    logg('F7: Motor avviser FH-runde utenfor horisonten', 'GJENSTÅR', gitt=[10])
for field in ['wc_runder', 'tc_runder']:
    stopp('Motor avviser ' + field, lambda: a.Motor(u, pr, **{field: [6]}))
for field in ['wc', 'tc']:
    stopp('Motor.bane avviser ' + field, lambda: m.bane(u.ORIG, **{field: 6}))
stopp('Motor avviser FH nå i tilgjengelighetslisten', lambda: a.Motor(u, pr, fh_runder=[6]))
stopp('Motor.bane avviser FH nå', lambda: m.bane(u.ORIG, fh=6))
stopp('Motor.faste_planer avviser FH nå', lambda: m.faste_planer({'A': u.ORIG}, None, 6))
stopp('Motor.standardanalyse avviser fh_start nå',
      lambda: a.Motor(u, pr, fh_start=6, fh_runder=[]).standardanalyse(maks_bytter=0, logg=lambda s: None))
# Rene kollisjonstilfellet når begge chips faktisk er tilgjengelige.
p = m.bane(u.ORIG, fh=7, full=True)
stopp('Motor.alternativ avviser BB=FH med tilgjengelige chips', lambda: m.alternativ('A', p, 7))
stopp('Motor.faste_planer avviser utilgjengelig FH', lambda: m.faste_planer({'A': u.ORIG}, 8, 9))

# Grense ved R20: BB nå er lovlig, FH bare fra neste runde; hele vinduet til R38 kan prognostiseres.
u20, md20, pr20 = a.liga(runde=20, slutt=21, kommende={20: [(1, 2), (3, 4), (5, 6)], 21: [(2, 1), (4, 3), (6, 5)]})
w20 = a.skriv_uke(u20, 'chips-r20-uke')
o20 = dict(o, runde=20, horisont_til=21, chips={'BB': [20], 'FH': [21]}, felles_chip={'BB': 20, 'FH': 21})
r20 = a.kj(w20, o20)
assert r20['kontroll']['status'] == 'OK' and r20['kontroll']['felles_BB'] == 20 and r20['kontroll']['felles_FH'] == 21
assert r20['planer']['A']['rows'][1]['chip'] == 'FH'
logg('R20-vindu: BB20/FH21 gjennom full CLI-funksjon', maks_avvik=r20['kontroll']['maks_avvik_gjenregning'])
for slutt in [29, 38]:
    rr = a.kj(w20, dict(o20, horisont_til=slutt), bare_poeng=True)
    assert rr['uke'].slutt == slutt
    logg('R20 horisont godtas', slutt=slutt)
stopp('R20 til R39 stoppes av CLI', lambda: a.kj(w20, dict(o20, horisont_til=39), bare_poeng=True))
stopp('FH20 stoppes av CLI', lambda: a.kj(w20, dict(o20, chips={'BB': [], 'FH': [20]})))
stopp('FH20 stoppes av Motor', lambda: a.Motor(u20, pr20, fh_runder=[20]))

# Direkte Motor avviser eksplisitte chipdatoer utenfor horisonten, både ved sesongvindu og chipvindu.
for fra, til in [(19, 20), (38, 39)]:
    bad, mm, pp = a.liga(runde=fra, slutt=til,
                        kommende={fra: [(1, 2), (3, 4), (5, 6)], til: [(2, 1), (4, 3), (6, 5)]})
    try:
        bm = a.Motor(bad, pp, bb_runder=[til], fh_runder=[])
        _, rows = bm.faste_planer({'A': bad.ORIG}, til, None)
    except (ValueError, AssertionError) as e:
        logg('F7: direkte Motor på tvers av vindu/sesong', 'RETTET', melding=str(e), fra=fra, til=til)
    else:
        logg('F7: direkte Motor på tvers av vindu/sesong', 'GJENSTÅR', fra=fra, til=til,
             BB=rows[0]['BB'], poeng=rows[0]['blend_horisont'])

# FT/vekt også gjennom full kjøring, ikke bare konstruktøren.
for extra in [dict(ft_folsomhet=[-1]), dict(vekt_codex=2), dict(gratisbytter=1.9)]:
    try:
        rr = a.kj(w, dict(o, **extra))
    except (ValueError, AssertionError) as e:
        logg('F2: full CLI med ugyldig tall', 'RETTET', oppsett=extra, melding=str(e))
    else:
        detail = {}
        if 'ft_folsomhet' in extra:
            detail['trekk_rull'] = a.les_csv(w / 'motor/ft_folsomhet.csv')[0]['poengtrekk_runde']
        logg('F2: full CLI med ugyldig tall', 'GJENSTÅR', oppsett=extra,
             status=rr['kontroll']['status'], faktisk_FT=rr['planer']['A']['FT'], **detail)

# F1: utilgjengelig FH kan fortsatt brukes i selve bane/alternativ og følsomheten.
empty = a.Motor(u, pr, bb_runder=[], fh_runder=[])
for name, fn in [('bane/alternativ', lambda: empty.alternativ('A', empty.bane(u.ORIG, fh=7), None)),
                 ('ft_folsomhet', lambda: empty.ft_folsomhet({'A': u.ORIG}, None, 7, [2]))]:
    try:
        fn()
    except (ValueError, AssertionError) as e:
        logg('F1: utilgjengelig FH i ' + name, 'RETTET', melding=str(e))
    else:
        logg('F1: utilgjengelig FH i ' + name, 'GJENSTÅR', fh_runder=[], FH=7)
logg('Chipkontroll ferdig', sekunder=round(time.monotonic() - start, 2))
