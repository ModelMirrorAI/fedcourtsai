# Evaluation — claude-baseline

## Cell

Cert-stage cell (`stage: cert`, `moment: cvsg`) for *Aldridge v. Regions Bank*, No. 25-590. Outcome: **denied** on 2026-10-13 (`actual_granted` 0), after three distributions; no noted dissent from denial. All three candidates predicted `denied` and froze `band: high` under `sal-v4`, so the segment base rate, `base_rate_basis` and Brier skill are the harness's stamp (the stamped segment base rate) and I write none of them; `correct` and `brier_score` below are my independent reads for the stamp to compare. Votes are not scored on a cert cell. No semantic set is declared on a cert cell, so no `semantic_grades` block. The forecast document and claims block are not graded here.

**Leakage.** All three are `forward` cells: snapshot cut 2026-04-07, predictions written 2026-09-18, outcome on 2026-10-13. Nothing any candidate could retrieve on 2026-09-18 disclosed a disposition that did not yet exist; I found no retrieved item dated on or after resolution and no reasoning reading the outcome. Graded `not_applicable`, `leakage_suspected: false`.

**Big case (my read, 0.35).** A real, acknowledged split on ERISA surcharge, but a top-hat plan / rabbi-trust vehicle with a disputed fiduciary threshold; denied quietly after the SG recommended denial. Specialist significance.

## Scores

- `correct` = 1 (predicted `denied`, actual `denied`).
- `brier_score` = (0.16 − 0)² = **0.0256**.
- `reasoning_quality` = **0.85**.

## Assessment

The strongest analysis of the three. It anchored on the prior-Term high-band pool (~35%) and the CVSG cut, then made the decisive move a forward cell permits: it retrieved the Solicitor General's 2026-08-31 invited brief (post-cutoff, pre-resolution — legitimate forward signal, disclosed) and correctly identified it as the largest update. It read the brief accurately — error conceded on QP1 but poor vehicle (top-hat exemption, unresolved CIGNA fiduciary-status threshold, Aramark vacated for en banc rehearing, QP2 unconflicted) — and cross-checked that the vehicle problems were already visible in the petition, the Sixth Circuit's opinion, and the BIO rather than taking the SG's word alone. It also weighed the pull the other way (response requested after waiver, CVSG interest, conceded split) and explained why it stopped at ~0.16 rather than ~0.10. The outcome — quiet denial following the SG — is the scenario it described.

Deductions: the conditional grant rate given an SG denial recommendation is from memory, not a committed figure (honestly flagged), and it did not read the supplemental reply. Its 0.18 conditional chance of separate writing was modestly high in hindsight, but that is not a reasoning flaw.
