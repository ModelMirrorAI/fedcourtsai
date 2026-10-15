# Evaluation — codex-baseline

## Cell

Cert-stage cell (`stage: cert`, `moment: cvsg`) for *Aldridge v. Regions Bank*, No. 25-590. Outcome: **denied** on 2026-10-13 (`actual_granted` 0), after three distributions; no noted dissent from denial. All three candidates predicted `denied` and froze `band: high` under `sal-v4`, so the segment base rate, `base_rate_basis` and Brier skill are the harness's stamp (the stamped segment base rate) and I write none of them; `correct` and `brier_score` below are my independent reads for the stamp to compare. Votes are not scored on a cert cell. No semantic set is declared on a cert cell, so no `semantic_grades` block. The forecast document and claims block are not graded here.

**Leakage.** All three are `forward` cells: snapshot cut 2026-04-07, predictions written 2026-09-18, outcome on 2026-10-13. Nothing any candidate could retrieve on 2026-09-18 disclosed a disposition that did not yet exist; I found no retrieved item dated on or after resolution and no reasoning reading the outcome. Graded `not_applicable`, `leakage_suspected: false`.

**Big case (my read, 0.35).** A real, acknowledged split on ERISA surcharge, but a top-hat plan / rabbi-trust vehicle with a disputed fiduciary threshold; denied quietly after the SG recommended denial. Specialist significance.

## Scores

- `correct` = 1 (predicted `denied`, actual `denied`; P(grant) 0.42 < 0.5).
- `brier_score` = (0.42 − 0)² = **0.1764**.
- `reasoning_quality` = **0.6**.

## Assessment

Careful and well-documented. It computed the prior-Term high-band pool correctly (314/898 ≈ 35%), explicitly avoided double-counting the CVSG and terminal relist cuts, read the petition, the Sixth Circuit's opinion and the BIO closely, and checked Amara and Montanile's footnote 3 against the actual opinions. It identified the vehicle problems that decided the case — top-hat exemption, contested fiduciary status, the panel's doubt that any violation was alleged, and the unconflicted QP2 — and called the BIO's wait-for-a-better-vehicle argument "persuasive".

The weakness is the direction of the final step: having found real vehicle defects and a pending Aramark en banc rehearing it did not check, it still adjusted *upward* from the anchor to 0.42, on the strength of the conflict — which the CVSG anchor already reflects. It also chose to restrict itself to the frozen record and not look up the current docket, though the cell was forward with unrestricted retrieval; it named the unobserved government recommendation as its largest uncertainty, and the SG's brief recommending denial was public by then. That restriction is conservative rather than wrong, but it left the most decisive available signal unread, and the upward adjustment is not well supported by its own analysis.
