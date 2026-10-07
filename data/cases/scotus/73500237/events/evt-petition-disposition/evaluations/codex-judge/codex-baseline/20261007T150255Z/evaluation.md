# Evaluation: codex-baseline

## Outcome and numerical scores

The cert-stage outcome records `denied` on October 5, 2026, with `actual_granted = 0`. The candidate's `denied` label matches, so **correct = 1**. Its 0.015 grant probability gives **Brier = 0.000225**. Denial supplies no explanation adopting or rejecting any particular legal argument.

The prediction's frozen context supplies `baseline`, `sal-v4`, and Term 2025. The committed statpack matches sal-v4; the proper basis is **risk_set**. I pool the bracketed baseline reached percentages for all eight displayed strictly prior Terms: 2017 (4.7%, n=1643), 2018 (4.6%, n=1524), 2019 (4.6%, n=1399), 2020 (4.5%, n=1739), 2021 (5.6%, n=1500), 2022 (5.8%, n=1192), 2023 (5.9%, n=1312), and 2024 (5.7%, n=1271). Their rate-weighted sum is 592.925 over 11,580, giving **segment_base_rate = 0.05120250431778929** and **Brier skill = 1 - 0.000225 / segment_base_rate^2 = 0.9141777072871345**.

These are rounded, denial-reweighted published estimates, not integer grant counts. The candidate reports using the corresponding unrounded JSON entries for 593/11,580; that tiny difference is a precision distinction, not an incorrect population choice. My score follows the prompt's displayed Markdown table and is approximate at that table's precision. The table renders 10 of 10 Terms, with 2025 and 2026 excluded; no truncated-window flag is warranted. No fresh corpus census or broad performance claim is made.

## Reasoning quality: 0.92

This is a strong, case-specific explanation rather than a post hoc defense of the correct label. It separates a claim of process liability from a lost accommodation, distinguishes the petitioner's allegations from the lower court's account, and identifies the two alternative grounds appearing in the provisioned Appendix A, pages 8a-12a. It also notices the panel's affirmative statement of good-faith collaboration, which makes a supposed holding that bad faith is irrelevant a poor description of the decision actually presented for review.

The rationale describes targeted checks of Strife and A.J.T. and explains why those authorities would not automatically remove this vehicle's qualification and reasonable-reassignment obstacles. Those checks are reflected in the staged retrieval record; I do not independently reconstruct the full external results from their digests. The analysis appropriately treats the waiver as modest evidence, not as an authoritative merits response, and expressly distinguishes terminal relist statistics from prospective hazards. Its frozen-version and strictly-prior-Term baseline use is careful.

The remaining limitations are the judgmental adjustment from roughly 5.1% to 1.5%, unresolved preservation and pleading questions, and absence of a respondent's substantive presentation. A single correct outcome cannot validate those probabilities. The high quality score rests on transparent, discriminating analysis, not on agreement with the ultimate denial or on retrieval volume.

The forecast document and quantitative claims were read for context only and are not included in `reasoning_quality`. Claim scores belong to the harness. Cert-stage vote accuracy and semantic grades are omitted. No independent big-case assessment is supplied.

## Leakage assessment

The log identifies forward mode and 31 September 17 calls, with 29 captured results and two unobserved web calls (coverage 29/31). The two web query slices concern earlier A.J.T. material. Their unobserved markers mean the returned content cannot be inspected, not that the searches returned nothing; the candidate's no-payload account is only its disclosure. The other documented authority checks concern earlier decisions, and the local reads concern the September 17 snapshot, petition, and aggregate context.

No visible query or reasoning passage reveals this petition's later disposition. The prediction and recorded calls precede the October 5 resolution, and the provisioned evaluator snapshot independently records that date. The broad uncertainty of uncaptured results does not itself establish outcome leakage. I record `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`.
