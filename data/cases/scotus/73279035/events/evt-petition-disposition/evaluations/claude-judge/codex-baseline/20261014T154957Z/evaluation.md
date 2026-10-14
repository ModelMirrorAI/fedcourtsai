# Evaluation — codex-baseline

## Cell

Cert-stage petition disposition, *Jerry Aldridge, et al. v. Regions Bank* (No. 25-590). Outcome: **denied** on 2026-10-13 (`actual_granted` 0), after three distributions and a CVSG (2026-04-06); no noted dissent from denial. The prediction froze `band: high` under `sal-v4`, so the segment base rate, `base_rate_basis` and Brier skill score are the harness's risk-set stamp; I leave them null and compare only against "the stamped segment base rate". Votes are not scored on a cert cell; no semantic set is declared, so no `semantic_grades` block.

## Score

- Predicted **denied**, P(grant) = 0.16 → `correct` = 1, Brier = 0.16² = **0.0256**.

## Reasoning quality: 0.85

Disciplined and well-calibrated. It explicitly separates its anchor (the `sal-v4` high-band reached rate pooled over OT2017–OT2024, computed from the unrounded statpack figures) from population-shape cuts (CVSG, relist buckets, modern cert, originating circuit), and correctly explains why neither the whole-docket rate nor a re-addition of CVSG/distribution signals is appropriate — avoiding double-counting. It read the SG's CVSG brief and petitioners' supplemental reply from the snapshot's own URLs and cited them by page; it identified the government's denial recommendation as the decisive downward signal while recording what the government conceded (the conflict, the Sixth Circuit's error), engaged the BIO's top-hat and liability objections, and noted the vacatur of the *Aramark* panel decision. It also explicitly declined to adopt respondent's overstatement that no conflict exists — a sign of reading the sources critically rather than echoing one side.

Discounts: the 16% is openly a judgmental adjustment rather than a conditioned rate, and the narrative could have weighed precedent for how often the Court grants over an SG deny recommendation; the prose is occasionally more procedural than analytical. Its legal reasoning — the Court would prefer a vehicle without the plan-specific fiduciary-status complication — is precisely what the denial is consistent with, though an unexplained denial cannot confirm the reason, as the candidate itself notes.

## Leakage

Forward cell (log `mode` forward). Prediction created 2026-09-18; the only external retrievals were the SG brief (8/31/2026) and the supplemental reply (9/16/2026), both predating resolution. One shell `find` names `data/qp-topics` only in a `-not -path` exclusion, which opens nothing there and is not a read. `not_applicable`, `leakage_suspected` false.
