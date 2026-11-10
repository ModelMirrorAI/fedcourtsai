# gemini-baseline — evaluation

Cert-stage, arrival-moment, forward cell. Outcome: petition **denied** on 2026-11-09 (`actual_granted` 0) after a respondent waiver (Aug 25, 2026) and a single distribution for the 11/6/2026 conference; no CVSG, no relist, no noted dissent. The segment base rate, its basis and the skill score are the harness's to stamp; this write-up quotes no rate of its own. The claims block is scored in code and not graded here. No semantic set is declared on a cert cell.

## Score
- Predicted `denied` at P(grant) = 0.01 → `correct` = 1, `brier_score` = 0.0001.

## Reasoning quality — 0.60
The direction and the main drivers are right: fact-bound QPs, no circuit split alleged, and a Rule 56(d)/summary-judgment posture that makes a poor vehicle. But the analysis is thin. It quotes the anchor only as "roughly 6%" and gives no Term window. It never engages the decision below (an unpublished, unreasoned per curiam), the strongest vehicle signal on the record. Nor does it show that the petition text was read beyond the QPs. The rationale reasons about a relist ("low ... second look") for a claim that, at zero distributions, is about the first distribution. That misreads the claim's frame, though the claim itself is scored in code and not here.

## Predicted reasoning — 0.50
The central claims were: denial without relists, no CVSG, and a small chance of a statement or dissent that did not materialize. All were borne out, but they are generic and commit to little beyond the modal outcome. They give no timing, no conference, and no response posture. The QP-selection content is conditional on a grant that did not happen.

## Leakage
Forward (predicted 2026-08-16, resolved 2026-11-09). Every call is `unobserved` (coverage 0.0, an engine-shape fact), so each was graded on its query: local reads of the prompt, schema, provisioned record and statpack, and validation. No call targeted outcome material. `not_applicable`, not suspected.

## Big case
0.12. This is a fact-bound private Title VII accommodation dispute with no split.
