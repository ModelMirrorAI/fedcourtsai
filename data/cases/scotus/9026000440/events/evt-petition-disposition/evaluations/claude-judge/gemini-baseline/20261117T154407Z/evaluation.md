# Evaluation — gemini-baseline, Jabateh v. United States (No. 26-440), cert stage

**Outcome:** petition denied on 2026-11-16 after one distribution, with no response call, no CVSG and no noted dissent.

**Prediction:** `denied`, P(grant) = 0.02. `correct` = 1; `brier_score` = 0.000400. The segment base rate and skill score are the harness's to stamp. No votes are scored on a cert cell, and no semantic set is declared, so there is no `semantic_grades` block.

## Reasoning (`reasoning_quality` = 0.85)

The strongest rationale of the three. It shows the pooled anchor Term by Term, sets it beside the terminal baseline rate, the Third Circuit cut and the zero-amicus cut, and then decomposes the headline as P(response call) 8% times P(grant after response) 25%, which reproduces the 0.02 exactly. The downward factors are well supported from the record: the waiver, the non-precedential opinion, the petition's own concession that the decision below "appears to be unique", the 2021 cert denial on the direct appeal (verified in the corpus), and the trial record. It also names the government's best counterargument (*Frady*'s higher hurdle on collateral review), which the petition does not.

The account of why the petition is not at near-zero odds is accurate to the appendix: the panel refused the change-in-law exception because the favourable construction came in the petitioner's own direct appeal. Weaknesses are small. The 25% conditional grant rate after a response is asserted rather than sourced, and the statement that the Court "will not" grant without a response call is put as a rule where it is a strong practice. A 0.85 `confidence` on a 0.02 forecast is unexplained.

## Predicted reasoning (`predicted_reasoning_quality` = 0.8)

Central claims: denial without a response call; the denial arriving on the 16 November order list; no further distribution; no CVSG; no separate writing. All five held. The grant-conditional forecast (a narrow vacatur holding that a not-"obvious" plain-error ruling is not an adverse merits adjudication) is specific but conditional on a grant that did not occur, so it earns nothing either way.

This document commits a little further than the others by naming the order-list date, which the docket bears out exactly. It stays short of the top anchor because the outcome it called is the heavy favourite on this record.

## Leakage

Forward cell: prediction run 2026-10-30 on the 2026-10-30 snapshot, before the 2026-11-16 denial. Every logged call is outcome_only, so results were not seen and the grade rests on the queries and prose: file reads of the provisioned record and statpack, fedcourts queries for docket numbers 20-1369 (the 2021 direct-appeal petition) and 26A102 (the extension application), and a CourtListener opinion search on the caption 'Jabateh'. The caption search could in principle reach this case, but it ran 17 days before the denial, retrieval.md reports only the 2018 and 2020 lower-court opinions, and nothing in the prose presupposes the result. No read under data/qp-topics/. Graded `not_applicable`; `leakage_suspected` = false.

## Big case

My read is 0.12: one prisoner's collateral-review petition from a non-precedential ruling with no split, denied without comment.
