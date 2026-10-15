# Evaluation — gemini-baseline

## Cell

Cert-stage petition disposition, *Jerry Aldridge, et al. v. Regions Bank* (No. 25-590). Outcome: **denied** on 2026-10-13 (`actual_granted` 0), after three distributions and a CVSG (2026-04-06); no noted dissent from denial. The prediction froze `band: high` under `sal-v4`, so the segment base rate, `base_rate_basis` and Brier skill score are the harness's risk-set stamp; I leave them null and compare only against "the stamped segment base rate". Votes are not scored on a cert cell; no semantic set is declared, so no `semantic_grades` block.

## Score

- Predicted **granted**, P(grant) = 0.75 → `correct` = 0, Brier = (0.75 − 0)² = **0.5625**.

## Reasoning quality: 0.20

The forecast rests on one decisive premise that turned out false: that the Solicitor General's invited brief "likely recommended granting certiorari." The candidate admits it never read the brief (the CourtListener document search failed and its one web search's result is unobserved in the log), yet it moved from its stated baseline to 0.75 entirely on that guessed recommendation. The brief was on the public docket and readable; the United States in fact recommended denial on vehicle grounds (confirmed against the provisioned `record/documents/sg-invited-brief.txt`: "The petition for a writ of certiorari should be denied") (a top-hat plan exempt from ERISA fiduciary rules, disputed fiduciary status of a rabbi-trust administrator, and the Fifth Circuit's *Aramark* panel decision vacated for en banc rehearing). Treating an unverified guess about the single most important signal as near-certain is the core defect.

Secondary problems: the baseline it quotes ("23.0% … for the 2025 Term") is the case's own Term rather than a pool of Terms strictly before it, so the anchor is drawn from the wrong window; it does not engage the brief in opposition's vehicle objections (top-hat exemption, the Sixth Circuit's doubts that any plan term was violated); and "a deep circuit split requires a merits opinion" is asserted without weighing the vehicle. It does correctly identify the question and the existence of a split, and is candid that its main uncertainty is the SG's text — which is why the score is not lower.

## Leakage

Forward cell (log `mode` forward). Prediction created 2026-09-18, three-plus weeks before the 2026-10-13 denial. Calls: MCP docket / recap-document lookups and one web search, all `unobserved`; nothing dated at or after resolution and the reasoning predicts the opposite outcome. `not_applicable`, `leakage_suspected` false.
