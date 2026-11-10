# Evaluation: gemini-baseline, scotus/9526000560 evt-motion-disposition

## Cell

This is an **interim** cell: the Solicitor General's application 26A560 to stay the W.D. Tex. preliminary injunction against border-barrier construction in the Big Bend Sector. `outcome.json` records `interim_reading: granted`, `interim_granted: 1`, resolved 2026-11-09. The Court granted the stay in full in a short per curiam, holding that a "major-questions-doctrine claim" alleges statutory excess and not a constitutional violation (*Dalton v. Specter*), so IIRIRA §102(c)(2)(A) bars it. Only Justice Jackson is noted as voting to deny. The segment base rate and the skill score are the harness's: `stamp-cell` pools the substantive-slice grant rate over application-Terms strictly before the prediction's. I write neither and quote no rate of my own. `vote_accuracy` is omitted because cert and interim votes are never scored. No semantic set is declared on an interim cell, so there is no `semantic_grades` block. The staged per curiam (`record/opinion/writings/OT2026-2/01-per-curiam.txt`) is used only to check the forecast document's claims about what the decision would hold.

## Score

The candidate predicted `granted` at P = 0.82. That is correct, with a Brier score of (0.82 − 1)² = 0.0324.

## Reasoning quality (0.70)

The legal analysis is strong and lands on the Court's actual ground. The candidate identified that the injunction rests entirely on treating the major-questions doctrine as a constitutional cause of action. It predicted a majority would read the doctrine as a statutory canon, and that §102(c)(2)(A) bars the claim. It also stressed the exclusive certiorari route under §102(c)(2)(C). It sensibly conditioned the generic interim pool on applicant type, using a small corpus-derived set of OT2026 SG stay applications (5 of 6 granted), and it reasoned explicitly about the denial-first resolution of a partial grant.

Two things cost it:

1. **Wrong base-rate figures.** The pool it reports (OT2025 25/148, OT2024 23/113, pooled 48/261 = 18.4%; n = 315 substantive) does not match the statpack build it was placed against. I rebuilt that build with `statpack-at` (eb6830084a18, the same build as the committed pack), and it shows 17/226, 16/194 and 18/127 for 2025, 2024 and 2023, pooling to 51/547 ≈ 9.3% over 642 substantive applications. The candidate also misdescribes the section caption as "descriptive only", when that build says the rows ground the scored base rate. The headline probability rests mainly on the SG-conditioned adjustment, so this did not move the forecast much. It is still a factual error in the anchor.
2. **Weight on grounds the Court did not use.** It gave substantial weight to *CASA* overbreadth and *Sierra Club*, which the Court did not rely on.

## Predicted reasoning (0.70)

I treated these as central, in the order the document weights them:

- **Borne out:** the unqualified stay pending cert in standard form, with no summary reversal.
- **Borne out, specifically:** the ground, that the major-questions doctrine is a statutory canon and not a constitutional claim. This is exactly the per curiam's holding.
- **Held only in direction:** *CASA*/*Sierra Club* equities. The equities did favor the government, but the Court used neither case.

The secondary claims failed:

- **Vote:** it called a 6–3 lineup with three noted dissents. Only Justice Jackson noted a dissent.
- **Timing:** it forecast 7–14 days. The Court took 19.

A specific, correct disposition and ground with a missed lineup and timing sits around 0.7.

## Leakage

Forward cell: `not_applicable`. The candidate's live query of the open 26A560 row (response requested Oct 22) and the district-court filings it read (dated on or before Oct 21) predate the Nov 9 resolution. These are legitimate forward signal, and the candidate disclosed them openly. Every logged call is result-unobserved, so I graded them on their queries. None sought post-resolution material.

## Big case

0.70: my own read of the stakes, explained in `big_case.notes`.
