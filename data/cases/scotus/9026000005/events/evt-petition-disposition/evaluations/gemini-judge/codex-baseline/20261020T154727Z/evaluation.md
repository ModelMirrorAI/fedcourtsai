# Evaluation of `codex-baseline` — `scotus/9026000005` (`evt-petition-disposition`)

## Outcome & Quantitative Summary

- **Stage:** `cert` (frozen `context.band`: `elevated`, `sal-v4`; segment base rate and Brier skill score are harness-stamped against the stamped segment base rate).
- **Predicted vs. Actual Disposition:** Predicted `denied` (`P(grant) = 0.12`) vs. actual `denied` (`actual_granted = 0`, resolved October 19, 2026, with no noted dissent from denial and `distribution_count = 2`).
- **Accuracy & Brier Score:** `correct = 1`, `brier_score = 0.0144`, improving on the stamped segment base rate.

## Reasoning Quality (`0.86`)

`codex-baseline` presented a structured, methodologically disciplined analysis in `reasoning.md`:

1. **Procedural & Statistical Discipline:** `codex-baseline` accurately parsed the docket sequence—noting that the August 5 distribution for the September 28 conference was interrupted by the August 13 call for a response and September 14 BIO, so the September 30 entry for the October 16 conference did not represent a post-conference relist—and carefully distinguished terminal relist/CVSG slices from forward increment hazards.
2. **Doctrinal Engagement with Both Questions Presented:** `codex-baseline` addressed both QP 1 (the NLRA's separation of prosecutorial authority in the General Counsel from adjudication in the Board) and QP 2 (severing purported residual executive functions rather than the removal restriction), explaining why *Trump v. Slaughter* and existing severance doctrine (*Seila Law*, *Free Enterprise Fund*) undermined both theories and made a GVR unlikely when the D.C. Circuit had already ruled for the government.
3. **Where It Lagged:** Unlike `claude-baseline`, `codex-baseline` did not use CourtListener MCP to inspect the *Slaughter* opinion directly, treating the BIO's description of *Slaughter* as an unverified advocate's account. That epistemic caution led `codex-baseline` to retain a relatively high `0.12` grant probability (including `0.060` for grant-and-summary-affirmance and `0.042` for a GVR), underweighting how conclusively *Slaughter* and the June 30, 2026 denial in the consolidated companion case (*Harris v. Bessent*, No. 25-1110) foreclosed further review.

## Leakage Assessment

- **Mode:** `forward` (`2026-09-30`, before the October 16, 2026 conference and October 19, 2026 denial).
- **Findings:** `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, `leakage_suspected = false`. The retrieval log (`result_capture_coverage = 0.926`) shows local reads of the provisioned `2026-09-30` snapshot, filings, and statpack, plus two `unobserved` web-search queries for general Supreme Court Rule 10 text (`site.supremecourt.gov "Rule 10" "compelling reasons"` and `2023RulesoftheCourt.pdf`). Neither query sought case-specific or outcome-revealing material.
