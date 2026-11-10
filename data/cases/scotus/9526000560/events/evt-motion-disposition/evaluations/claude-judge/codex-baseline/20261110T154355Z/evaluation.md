# Evaluation: codex-baseline, scotus/9526000560 evt-motion-disposition

## Cell

This is an **interim** cell: the Solicitor General's application 26A560 to stay the W.D. Tex. preliminary injunction against border-barrier construction in the Big Bend Sector. `outcome.json` records `interim_reading: granted`, `interim_granted: 1`, resolved 2026-11-09. The Court granted the stay in full in a short per curiam, holding that a "major-questions-doctrine claim" alleges statutory excess and not a constitutional violation (*Dalton v. Specter*), so IIRIRA §102(c)(2)(A) bars it. Only Justice Jackson is noted as voting to deny. The segment base rate and the skill score are the harness's: `stamp-cell` pools the substantive-slice grant rate over application-Terms strictly before the prediction's. I write neither and quote no rate of my own. `vote_accuracy` is omitted because cert and interim votes are never scored. No semantic set is declared on an interim cell, so there is no `semantic_grades` block. The staged per curiam (`record/opinion/writings/OT2026-2/01-per-curiam.txt`) is used only to check the forecast document's claims about what the decision would hold.

## Score

The candidate predicted `granted` at P = 0.86. That is correct, with a Brier score of (0.86 − 1)² = 0.0196, the best of the three.

## Reasoning quality (0.82)

The anchor is the correct strictly-prior pool: 51/547 = 9.32%, matching the placed build (`statpack-at` eb6830084a18). The candidate explicitly excluded Term 2026 and the pack-level rate, and noted the selection caveats.

The case-specific adjustment is well reasoned. It saw that the review scheme preserves constitutional claims and bars statutory ones, while the injunction rests on a statutory-authority objection. It independently verified *Dalton v. Specter* (511 U.S. at 472–474) for the statutory-versus-constitutional distinction, and that is exactly the passage the per curiam cites.

It was careful about what it did not know:

- It acknowledged the one-sided record.
- It declined to over-rely on *Sierra Club* or on recent precedents it could not verify.
- It separated P(unqualified grant) from the summary-reversal alternative.

The downward adjustments are named, though not separately quantified. This is the most disciplined of the three analyses.

## Predicted reasoning (0.90)

Every central claim held:

- **Borne out:** an unqualified stay pending cert.
- **Borne out, specifically:** the ground, that a statutory-authority objection cannot be converted into a constitutional claim by invoking the major-questions doctrine. This closely tracks the per curiam's "however it is labeled" reasoning.
- **Borne out:** a full-Court disposition between Oct 28 and Nov 11 (it came Nov 9).
- **Borne out:** the government's border-security and cost harms outweighing respondents' environmental and historic-resource harms.
- **Borne out:** a stay rather than summary reversal.

The document made no vote forecast. It sits just below the top anchor because one of its forecasts was hedged: it called for a "concise stay order", and the Court issued a short explanatory per curiam.

## Leakage

Forward cell: `not_applicable`.

- **Web searches:** two general-authority queries, uncaptured, so graded on their queries (the statute text and *Dalton*). Neither concerned this case.
- **CourtListener:** a lookup of *Dalton v. Specter* (1994).
- **Disposition:** nothing in the log sought this application's disposition.

## Big case

0.70: my own read of the stakes, explained in `big_case.notes`.
