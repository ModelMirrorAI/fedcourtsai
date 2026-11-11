# Evaluation of `gemini-baseline`

## Outcome and Quantitative Scoring

- **Stage:** `cert` (`evt-petition-disposition` on `scotus/9026000055`, *Sohilbhai Shaukatali Momin v. Todd Blanche, Attorney General*, No. 26-55).
- **Outcome:** Denied on November 9, 2026 (`actual_disposition: "denied"`, `actual_granted: 0`), off the first distribution (`distribution_count: 1`, `cvsg_date: null`, `noted_dissent_from_denial: false`).
- **Prediction:** `predicted_disposition: "denied"`, `probability: 0.015`.
- **Accuracy & Brier Score:** `correct = 1`, `brier_score = (0.015 - 0)^2 = 0.000225`.
- **Base Rate & Skill:** The harness stamps the segment base rate, basis, and Brier skill score from the committed statpack at stamp time. The candidate's base-rate use was graded against the statpack build in force at prediction time (`886549a3ac32`, `sha256:1d7fbb9fce0582c4e5a8b7dbbb54fb504532c2bdd7ef8b9946c8145115860bde`, retrieved via `fedcourts statpack-at`), which differs from the currently checked-out `metrics/statpack.json`.

## Reasoning Quality (`0.72`)

`gemini-baseline` produced a concise rationale (`reasoning.md`) that correctly identified the case's posture as a Fifth Circuit immigration petition and achieved the lowest Brier score (`0.000225`), but took a methodological shortcut in its base-rate anchoring:

1. **Conflating Terminal Relist Bucket with Forward Risk Set:** While noting the `baseline` salience band's reached rate from the statpack (`886549a3ac32`), `gemini-baseline` anchored its headline `P(grant) = 0.015` directly on the `relist-0` bucket's rate (`~1.2%` granted, `~1.7%` grant+GVR). As the statpack notes, the `relist-0` bucket is a *terminal* classification (petitions that never relisted before disposition), whereas a live petition at `distribution_count = 1` can still relist (`gemini-baseline` itself assigned `0.08` to `relist-increment`) and enter higher-grant-rate buckets.
2. **Sound Case-Type Identification:** Despite the lack of provisioned document texts at prediction time, `gemini-baseline` properly recognized the case as a routine Fifth Circuit immigration petition where the Solicitor General had already filed a Brief in Opposition (making `cvsg-increment = 0.0` appropriate).
3. **Brevity:** The analysis in `reasoning.md` was brief and did not weigh the voluntary BIO (filed without a call for response after two extensions) against the downward case-type factors as thoroughly as `claude-baseline`.

## Predicted reasoning (`0.62`)

In `predicted_reasoning.md`, `gemini-baseline` briefly and accurately stated the expected procedural path:
- **Disposition and Relists (borne out):** Expected denial at the first conference with no further relists (`actual_disposition = "denied"`, `distribution_count = 1`).
- **CVSG (borne out):** Expected no CVSG because the Solicitor General was already the respondent and had filed a Brief in Opposition (`cvsg_date = null`).
- **Dissent from Denial (borne out):** Expected no separate writing (`noted_dissent_from_denial = false`).

The document's central claims all held, though the forecast was very short (two paragraphs) and did not specify the conference or order-list timing as concretely as `claude-baseline` and `codex-baseline`.

## Leakage (`not_applicable`, `leakage_suspected: false`)

The prediction ran in `forward` mode on `2026-10-17`, well before the `2026-11-06` conference and `2026-11-09` denial. In `retrieval_log.json` (`result_capture_coverage: 0.0`, all calls `unobserved`), the query parameters show local reads of the `2026-10-17` snapshot and `metrics/statpack.md`, along with seven CourtListener MCP searches for docket numbers `26-55` and `25-60471` and party name `Momin` / `Sohilbhai`. Because the case was genuinely unresolved when the prediction ran, no outcome material existed to be leaked.

## Big-Case Read (`0.05`)

As confirmed by the Brief in Opposition (`record/documents/brief-in-opposition.txt`), this petition involved a fact-bound challenge to an unpublished Fifth Circuit ruling affirming the denial of an untimely BIA motion to reopen based on forfeited arguments regarding changed country conditions in India. It was denied on the first conference without dissent (`0.05`).
