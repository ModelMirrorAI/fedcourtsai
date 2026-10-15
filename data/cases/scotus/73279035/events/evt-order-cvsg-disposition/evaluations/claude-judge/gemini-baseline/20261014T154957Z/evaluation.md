# Evaluation — gemini-baseline

## Cell

Cert-stage cell (`stage: cert`, `moment: cvsg`) for *Aldridge v. Regions Bank*, No. 25-590. Outcome: **denied** on 2026-10-13 (`actual_granted` 0), after three distributions; no noted dissent from denial. All three candidates predicted `denied` and froze `band: high` under `sal-v4`, so the segment base rate, `base_rate_basis` and Brier skill are the harness's stamp (the stamped segment base rate) and I write none of them; `correct` and `brier_score` below are my independent reads for the stamp to compare. Votes are not scored on a cert cell. No semantic set is declared on a cert cell, so no `semantic_grades` block. The forecast document and claims block are not graded here.

**Leakage.** All three are `forward` cells: snapshot cut 2026-04-07, predictions written 2026-09-18, outcome on 2026-10-13. Nothing any candidate could retrieve on 2026-09-18 disclosed a disposition that did not yet exist; I found no retrieved item dated on or after resolution and no reasoning reading the outcome. Graded `not_applicable`, `leakage_suspected: false`.

**Big case (my read, 0.35).** A real, acknowledged split on ERISA surcharge, but a top-hat plan / rabbi-trust vehicle with a disputed fiduciary threshold; denied quietly after the SG recommended denial. Specialist significance.

## Scores

- `correct` = 1 (predicted `denied`, actual `denied`; its P(grant) of 0.35 sits below one-half).
- `brier_score` = (0.35 − 0)² = **0.1225**.
- `reasoning_quality` = **0.35**.

## Assessment

The rationale is a single paragraph that adopts the base rate (high-band pool ~35%, CVSG cut ~34.9%) and stops. Its pieces are not wrong, but the analysis is thin in three ways. (1) It calls the CVSG "a strong affirmative signal" while the anchor already conditions on it, without saying whether that moves the number — it doesn't, so the sentence does no work. (2) It names vehicle flaws as its main uncertainty but never examines the petition or BIO for them, although the top-hat exemption and disputed fiduciary status were plain in the provisioned documents and are what the case turned on. (3) Writing on 2026-09-18 in a forward cell, it says the SG's recommendation is still to come, when the SG had filed on 2026-08-31; with unrestricted retrieval permitted, a check of the docket would have found it. Treating the SG's position as unknown is defensible on the snapshot alone, but neither a case-specific adjustment nor a look at the record was attempted. The correct label comes from the base rate falling under 0.5, not from case analysis.
