# Siste beregningsrunde: WC8 mot WC11

**Anbefaling R8: Hold WC til R11. Szoboszlai → Tavernier nå; ingen trekk.**

## 1. Identiske chipdatoer

WC8 og B+WC11 er kjørt på nytt med samme BB/FH-par og samme R2-byttepolitikk. Begge søk får alle nominelle tropper som ekstra startpunkter; dette hindrer at en oversett finansieringskombinasjon blåser opp WC-fordelen. Endringen fra første søk står i sokekontroll_r3.csv. Alle fire felles par omfatter også hvert hovedløps valgte R2-par. «Eget beste» betyr beste av disse fire, ikke et bevist optimum over alle mulige chipdatoer.

| Poengsett | BB/FH felles | E | B_WC11 | E minus B |
|---|---|---:|---:|---:|
| codex | 15/9 | 702.0 | 697.1 | +5.0 |
| codex | 17/13 | 703.2 | 696.4 | +6.8 |
| codex | 19/13 | 703.6 | 696.8 | +6.8 |
| codex | 19/9 | 703.0 | 698.1 | +5.0 |
| repo_hybrid | 15/9 | 767.1 | 765.0 | +2.1 |
| repo_hybrid | 17/13 | 767.9 | 765.4 | +2.4 |
| repo_hybrid | 19/13 | 768.0 | 765.6 | +2.5 |
| repo_hybrid | 19/9 | 767.9 | 766.1 | +1.8 |

Eget beste, codex: E BB19/FH13 = 703.6; B BB19/FH9 = 698.1; forskjell +5.6.

Eget beste, repo_hybrid: E BB19/FH13 = 768.0; B BB19/FH9 = 766.1; forskjell +2.0.

At B leder til R15 med tidligere BB, viser ikke alene at E-fordelen skyldes chips; en tidligere chip flytter poeng frem i tid. Tabellen over isolerer datoene. Bytter og tropper kan fortsatt utvikles forskjellig som følge av selve WC-tidspunktet.

## 2. Ukjente nye fravær

300 parede trekk per p og poengsett, seed 7089878. Her brukes **BB17/FH13 i begge baner**, så skadeeffekten blandes ikke med ulik chipkalender. Kampresultater trekkes ikke: poengene er forventede FPL-poeng gitt det trukne fraværet.

| Poengsett | p | E snitt | B snitt | E minus B | E vinner | Paret MC-SE | B WC9/10 |
|---|---:|---:|---:|---:|---:|---:|---:|
| codex | 0.01 | 700.7 | 693.8 | +6.9 | 99.7% | 0.1 | 0.0% |
| repo_hybrid | 0.01 | 764.6 | 761.4 | +3.2 | 99.7% | 0.1 | 0.0% |
| codex | 0.02 | 698.6 | 691.5 | +7.1 | 99.3% | 0.1 | 1.3% |
| repo_hybrid | 0.02 | 761.6 | 757.8 | +3.8 | 100.0% | 0.1 | 1.0% |
| codex | 0.03 | 696.0 | 688.7 | +7.4 | 99.0% | 0.1 | 1.0% |
| repo_hybrid | 0.03 | 758.0 | 753.6 | +4.4 | 98.3% | 0.1 | 1.0% |

Paret MC-SE måler bare numerisk usikkerhet fra 300 fraværstrekk, ikke feil i spillerprognosene. Andelen E vinner er heller ikke sannsynligheten for å vinne i faktiske kampresultater. 10/90-persentiler, trekkostnader og forskjell mot p=0 står i CSV-en.

Forenklinger:

- Samme potensielle fravær for hver spiller/runde brukes i begge baner og begge poengsett. Det trekkes for hele kjøpsuniverset, også ikke-eide kandidater; man kan dermed ikke kjøpe en spiller som nettopp er kjent skadet. Dette utvider «eide spillere» til en felles fotballverden og unngår kunstig friske erstattere.
- Fra R9 får en frisk spiller nytt fravær med p per runde; varighet 1/2/3/6 runder med lik sannsynlighet, startunden inkludert. Ingen ny hendelse mens spilleren allerede er ute. Varigheten blir kjent når fraværet starter. Fremtidige hendelser er skjult for byttepolitikken.
- B bruker WC i R11, fremskyndet til R9/R10 når minst tre av troppens nominelle beste elleve er ute før bytter. Etter R11 er WC brukt i begge baner; å vente til R11 gir ikke WC-forsikring gjennom hele julen.
- Samme grådige neste-fire-runder-regel i begge baner: rull ved gevinst ≤1, maks fem FT; ved taket/R19 terskel null. Ett ekstra trekk tillates bare ved brutto gevinst >5. Vinduet stopper før planlagt WC, utelater FH og inkluderer BB. FT ved WC/FH bevares uten opptjening, som R2-hovedantakelsen.
- For kjøretid: seks beste + tre billigste kandidater per posisjon; WC/FH starter fra skadefrie referansetroppsmaler/reparert tropp/billig tropp og bruker bredde én, maks seks forbedringsbytter. Innkjøp må være tilgjengelige og passere R2-rollefilteret; eide korttidsskadde kan beholdes når kjent retur forsvarer det. Salgspriser, bank og klubbgrense kontrolleres.
- Ingen nye rolleendringer, prisendringer, endret kampprogram eller tilfeldig normalrotasjon. Kjent fravær gir null poeng og beste lovlige ellever velges fra resten. BB gir bare poeng for tilgjengelige spillere. Forventede minutter og bonus er fortsatt R2-antakelser.

### Kontroll av det enklere søket, uten nye fravær

| Poengsett | Fullt R2-søk E−B, BB17/FH13 | Lett MC-politikk, p=0 | Forskjell i margin |
|---|---:|---:|---:|
| codex | +6.8 | +6.8 | +0.0 |
| repo_hybrid | +2.4 | +2.4 | +0.0 |

p=0,02, codex: skadeverdenen flytter E−B med +0.3 poeng mot den samme lette politikkens p=0. Etter ±5-regelen: WC8 mot WC11 er **bedre**.

p=0,02, repo_hybrid: skadeverdenen flytter E−B med +1.3 poeng mot den samme lette politikkens p=0. Etter ±5-regelen: WC8 mot WC11 er **likeverdig**.

## 3. Sluttvurdering

Klassifisering ved hovedverdien p=0,02: **modellavhengig**. «Likeverdig» betyr innenfor ±5 poeng. Dette er en praktisk beslutningsgrense, ikke en statistisk test.

Jeg trekker tilbake den svake R2-anbefalingen om WC nå. WC8 har ikke en entydig fordel over fem poeng i begge hovedsimuleringer med lik chipkalender. Når gevinsten er så liten/modellavhengig, anbefaler jeg å beholde muligheten til å velge tropp med oppdatert informasjon i R11. Dette er et beslutningsskjønn ved liten margin, ikke en ekstra beregnet «informasjonsbonus».

Claude har rett i at rollestøy kan være større enn en ettpoengsmargin. Informasjonsverdi må likevel ikke dobbelttelles: forventet skadevern er nå simulert, og bedre benkedekning etter en tidlig WC kan også redusere skadetap. Nettovirkningen av skader trenger derfor ikke peke bare én vei.

R14–19-vurderingen er tatt med gjennom de faktiske kampene i Codex-poengene; repo-hybrid bruker Codex etter R13. COVs programskifte er dermed ikke ignorert. Fraværsmodellen øker ikke p særskilt i julen og simulerer ikke europeisk rotasjon: Claudes bekymring for BB i R17–19 er fortsatt en restusikkerhet, ikke et verifisert fratrekk.

Anbefalingen kan endres av nye bekreftede fravær/roller før R8-fristen, særlig hvis flere startere faller bort, eller hvis en ny felles tropp gir en klar >5-poengsfordel i begge poengsett. Ved hold: start Thiago foran Maguire, Haaland kaptein og Fernandes vice, som støttet i R2. Full oppstilling etter ett bytte står i rekonstruksjonen under.

Kjør: `/Users/simenflogstad/opt/anaconda3/bin/python3 samarbeid/gw08/codex/modell_r3.py`. Skriptet leser frosne R2-poeng, kompilierer bare funksjonsdefinisjoner fra R2-koden og tilføyer symmetriske starttropper; ingen R2-kjøring eller R2-skriving skjer. Alle nye filer har _r3. Ingen nett/installasjon.

**R8 etter ett bytte:** Verbruggen, Calafiori, Konsa, N.Williams, Mbeumo, B.Fernandes, Tavernier, E.Le Fée, Groß, Haaland, Thiago. Benk (keeper først, så utespillere i rekkefølge): Steele, Maguire, van Ewijk, Kusi-Asare. Bank £1,6m; to FT til R9.
