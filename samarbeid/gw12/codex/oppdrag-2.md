<task>
Fortsett i samme tråd. Du har levert `codex/analyse.md` for R12 med G_keep: Dasilva og Silva ut, Bogle og Justin inn, med kaptein De Cuyper og FH15.
Les først `samarbeid/gw12/claude/forslag.md` (Claudes forslag, skrevet før dine resultater) og `claude/kritikk-av-codex.md`.
Kritiser Claudes forslag og test innvendingene med beregninger. Bruk samme modell og samme spillerpoeng, uten modellendringer.
Skriv kortfattet, og prioriter rekkefølgen under hvis kvoten blir knapp.
</task>

<required_checks>
1. Regn Claudes forslag P: Ødegaard → Le Fée og Dasilva → Konsa (bank 0,5, 2 gratisbytter, FH15).
   Bruk samme byttepolitikk og eksakte autobytter, og vis R12, R12–R15 og R12–R19 i begge poengsett mot A og G_keep.
   Kjør også paret skadesimulering ved 2 % (100 verdener) for P mot G_keep.
2. Lag en fast-tropp-tabell for R12–R15 uten senere bytter: A, B, C, P og G_keep, med eksakte autobytter, begge poengsett og FH15.
   Hensikten er å se hvor mye av gevinsten mot A som kommer fra R12-byttene og hvor mye som kommer fra senere modellbytter.
3. Finn beste plan med 1 bytte som selger Dasilva (bare forsvarere til 4,4 eller mindre), og sammenlign med B og G_keep.
   Test også Dasilva, Silva → Justin og Muharemović eller Konsa hvis budsjettet tillater det (0,4 + 9,0 = 9,4).
4. Gi kapteinsrangeringen (topp 4, begge poengsett og blanding) for troppen du nå anbefaler.
5. Gi en konklusjon: hvilken R12-handling anbefaler du nå, og hvorfor fremfor P og fremfor å rulle?
</required_checks>

<action_safety>
Skriv bare i `samarbeid/gw12/codex/`, og ikke endre filene `spillerpoeng.csv` eller `minutter_antatt.csv`.
Ikke commit noe i git, og bruk Anaconda som før.
</action_safety>

<deliverables>
`codex/kontroll.md` på norsk, med tabeller for punkt 1–5, og `codex/kontroll_r12.csv` med tallene. Skriv `kontroll.md` tidlig og oppdater den underveis.
</deliverables>
