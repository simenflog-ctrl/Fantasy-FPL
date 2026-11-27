"""Uavhengig fasit for forventet lagpoeng: gå gjennom ALLE utfall av hvem som spiller, og bruk FPL-reglene rett fram.

Deler ingen kode med lag.py. Brukes bare i tester.

Regler:
  * En spiller som spiller, gir xp/pp poeng (forventet poeng gitt at han spiller). En som ikke spiller, gir 0.
  * Keeper: spiller ikke startkeeperen, kommer reservekeeperen inn hvis han spiller.
  * Utespillere: benken gås gjennom i rekkefølge. En benkespiller som spiller, erstatter den første startspilleren
    (i elleverens rekkefølge) som ikke spiller og ikke alt er erstattet, forutsatt at formasjonen etterpå har
    minst 3 forsvar, 2 midtbane og 1 spiss. Finnes ingen slik, står han over.
  * Kapteinen teller dobbelt. Spiller ikke kapteinen, teller visekapteinen dobbelt hvis han spiller.
  * Bench Boost: alle 15 teller, ingen bytter.
"""
import itertools

MIN = {2: 3, 3: 2, 4: 1}


def forventet(pos, xp, pp, ellever, benk, kaptein, vise, bench_boost=False):
    """pos/xp/pp: lister for de 15 i troppen. ellever: 11 plasser (keeper først). benk: [reservekeeper, b1, b2, b3]."""
    gitt = [xp[i] / pp[i] if pp[i] > 0 else 0. for i in range(15)]
    usikre = [i for i in range(15) if 0 < pp[i] < 1]
    total = 0.
    for utfall in itertools.product([0, 1], repeat=len(usikre)):
        spiller = [pp[i] >= 1 for i in range(15)]
        sanns = 1.
        for i, x in zip(usikre, utfall):
            spiller[i] = bool(x)
            sanns *= pp[i] if x else 1 - pp[i]
        if bench_boost:
            teller = list(range(15))
        else:
            teller = list(ellever)
            keeper = ellever[0]
            if not spiller[keeper] and spiller[benk[0]]:
                teller[0] = benk[0]
            form = {k: sum(1 for i in ellever[1:] if pos[i] == k) for k in (2, 3, 4)}
            erstattet = set()
            for b in benk[1:]:
                if not spiller[b]:
                    continue
                for plass, i in enumerate(ellever):
                    if plass == 0 or spiller[i] or i in erstattet:
                        continue
                    ny = dict(form)
                    ny[pos[i]] -= 1
                    ny[pos[b]] += 1
                    if all(ny[k] >= MIN[k] for k in MIN):
                        form = ny
                        erstattet.add(i)
                        teller[plass] = b
                        break
        poeng = sum(gitt[i] for i in teller if spiller[i])
        if spiller[kaptein]:
            poeng += gitt[kaptein]
        elif spiller[vise]:
            poeng += gitt[vise]
        total += sanns * poeng
    return total
