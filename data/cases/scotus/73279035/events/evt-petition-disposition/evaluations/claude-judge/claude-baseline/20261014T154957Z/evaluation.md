# Evaluation — claude-baseline

## Cell

Cert-stage petition disposition, *Jerry Aldridge, et al. v. Regions Bank* (No. 25-590). Outcome: **denied** on 2026-10-13 (`actual_granted` 0), after three distributions and a CVSG (2026-04-06); no noted dissent from denial. The prediction froze `band: high` under `sal-v4`, so the segment base rate, `base_rate_basis` and Brier skill score are the harness's risk-set stamp; I leave them null and compare only against "the stamped segment base rate". Votes are not scored on a cert cell; no semantic set is declared, so no `semantic_grades` block.

## Score

- Predicted **denied**, P(grant) = 0.30 → `correct` = 1, Brier = 0.30² = **0.09**.

## Reasoning quality: 0.85

A careful, well-sourced analysis. It anchored on the high-band `sal-v4` reached rate pooled over Terms strictly before OT2025 and cross-checked it against the paid-segment CVSG cut, correctly declining to double-count the relist cut. Its decisive move — retrieving and reading the United States' CVSG brief, a legitimate forward signal on the docket — is exactly right, and its summary of that brief (concedes the Sixth Circuit erred and that a conflict exists, but recommends denial as a poor vehicle; no conflict on the preemption question) drives a correct downward adjustment. It weighed both sides concretely: petitioners' supplemental reply and the Court's prior interest on one side, the vehicle problem, the pending en banc *Aramark* alternative, the 2024 denial in *Rose v. PSA Airlines*, and respondent's liability objection on the other.

Discounts: the step from ~35% to a "20–25% conditional on a deny recommendation" starting point is from general knowledge, which it flags; and 0.30 then sits *above* that conditional rate on arguments (the Court "plainly wants to reach" the question; a vehicle-only denial is "weak") that the outcome did not bear out — the Court followed the SG, as its own "historical pattern" paragraph suggested it usually does. The upward adjustment was somewhat generous, but the structure of the argument is sound and transparent, and it states where to discount it.

## Leakage

Forward cell (log `mode` forward; all calls captured). Prediction created 2026-09-18; retrieved the supremecourt.gov docket page (entries only through 9/16/2026, no disposition), the SG brief (8/31/2026), the supplemental brief (9/16/2026), the SCOTUSblog case page (no disposition) and a January 2026 blog post. All predate resolution; honest, complete disclosure in `retrieval.md`. `not_applicable`, `leakage_suspected` false.
