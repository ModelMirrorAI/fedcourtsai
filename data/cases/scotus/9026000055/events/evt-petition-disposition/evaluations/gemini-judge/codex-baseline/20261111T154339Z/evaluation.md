# Evaluation of `codex-baseline`

## Outcome and Quantitative Scoring

- **Stage:** `cert` (`evt-petition-disposition` on `scotus/9026000055`, *Sohilbhai Shaukatali Momin v. Todd Blanche, Attorney General*, No. 26-55).
- **Outcome:** Denied on November 9, 2026 (`actual_disposition: "denied"`, `actual_granted: 0`), off the first distribution (`distribution_count: 1`, `cvsg_date: null`, `noted_dissent_from_denial: false`).
- **Prediction:** `predicted_disposition: "denied"`, `probability: 0.05`.
- **Accuracy & Brier Score:** `correct = 1`, `brier_score = (0.05 - 0)^2 = 0.0025`.
- **Base Rate & Skill:** The harness stamps the segment base rate, basis, and Brier skill score from the committed statpack at stamp time. The candidate's base-rate use was graded against the statpack build in force at prediction time (`886549a3ac32`, `sha256:1d7fbb9fce0582c4e5a8b7dbbb54fb504532c2bdd7ef8b9946c8145115860bde`, retrieved via `fedcourts statpack-at`), which differs from the currently checked-out `metrics/statpack.json`.

## Reasoning Quality (`0.78`)

`codex-baseline` wrote a methodologically rigorous rationale (`reasoning.md`) that carefully respected the boundaries of the provisioned record and the statistical tables:

1. **Exact Base-Rate Pooling:** The candidate correctly identified the `sal-v4` `baseline` reached risk set across strictly prior Terms (2017–2025) from the statpack build in force at prediction time (`886549a3ac32`) and explained why marginal cuts (such as terminal relist or circuit tables) should not be treated as naive independent multipliers on top of the risk-set anchor.
2. **Overly Agnostic Treatment of Docket Signals:** While `codex-baseline`'s discipline in refusing to invent unprovisioned facts is commendable, the candidate left information on the table by declining to make even basic structural inferences from the docket (such as recognizing from the Attorney General respondent and Fifth Circuit `25-60xxx` docket sequence that this was a petition for review of a BIA immigration order) and by leaving `big_case_score` null rather than estimating low stakes from the procedural posture and lack of amicus or repeat-player involvement. Retaining the raw risk-set prior (`0.05`) without downward adjustment for a first-conference, no-amicus individual petition against the Attorney General yielded a slightly higher Brier score (`0.0025`) and zero lift over the stamped segment base rate.
3. **High Relist Probability:** Assigning `0.22` to `relist-increment` for a routine baseline petition at its first conference with no call for response or amicus support was somewhat high relative to the forward transition rate on first-distribution petitions.

## Predicted reasoning (`0.65`)

In `predicted_reasoning.md`, `codex-baseline` accurately predicted the central procedural outcomes:
- **Disposition and Timing (borne out):** Forecast denial by an unexplained order following the November 6, 2026 conference (resolved November 9, 2026).
- **Relists (borne out):** Predicted zero additional distributions as the modal path, though hedging with a 22% probability of at least one further distribution.
- **CVSG (borne out):** Correctly explained that no CVSG would issue (`0.1%`) because the federal respondent had already filed an opposition.
- **Dissent from Denial (borne out):** Predicted no noted dissent or separate statement (`1%`).

The forecast document is clear and accurate on the procedural mechanics, though slightly more generic and hedged on relists and subject-matter context than `claude-baseline`.

## Leakage (`not_applicable`, `leakage_suspected: false`)

The prediction ran in `forward` mode on `2026-10-17`, prior to the `2026-11-06` conference and `2026-11-09` denial. The retrieval log (`result_capture_coverage: 0.875`) shows local shell inspection of the `2026-10-17` snapshot, schemas, and statpack, plus four `unobserved` web-search/open calls for general Supreme Court Rules (`Rule 10`, `Rule 34.6`, `rules_guidance.aspx`, `2026RulesoftheCourt_WEB.pdf`). None of the queries targeted post-cutoff case outcomes, and the case was unresolved at the time of the run.

## Big-Case Read (`0.05`)

As shown by the Brief in Opposition (`record/documents/brief-in-opposition.txt`), the petition sought review of an unpublished Fifth Circuit decision affirming the BIA's denial of an untimely motion to reopen where the petitioner failed to meaningfully contest the agency's finding on changed country conditions in India. It is a routine, fact-bound individual immigration case (`0.05`).
