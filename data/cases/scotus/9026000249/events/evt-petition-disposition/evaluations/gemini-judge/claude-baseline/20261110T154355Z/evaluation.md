# Evaluation of claude-baseline

## Quantitative summary

- **Stage:** `cert` (`evt-petition-disposition` in `scotus/9026000249`, *Randy Quaid, et ux. v. Craig Granet, et al.*, No. 26-249).
- **Predicted disposition / probability:** `denied` (`probability = 0.004`, `granted = 0`).
- **Actual outcome:** `denied` (`actual_granted = 0`, resolved `2026-11-09`).
- **Correct:** `1` (`predicted_disposition == actual_disposition`).
- **Brier score:** `0.000016`.
- **Segment base rate and skill:** Left to the harness stamp (`stamp-cell` pools the stamped segment base rate and `brier_skill_score` from the committed statpack). To verify `claude-baseline`'s base-rate usage against the pack in force when the prediction ran (`20261015T142602Z`), I reconstructed statpack build `886549a3ac32bdba039691b6d2ca7dc57bb72561` (`sha256:1d7fbb9fce0582c4e5a8b7dbbb54fb504532c2bdd7ef8b9946c8145115860bde`, which differs from the currently committed `metrics/statpack.md`) via `uv run fedcourts statpack-at`. Evaluated against that build, `claude-baseline` properly pooled the `sal-v4` `baseline` band's bracketed `reached` (risk-set) rate across Terms 2017–2025 (strictly before OT2026) weighted by `n`, matching the methodology behind the stamped segment base rate.

## Reasoning quality (`0.85`)

`claude-baseline` produced a clear, well-structured, and methodologically sound rationale in `reasoning.md`:

1. **Base-rate discipline:** Correctly selected the `baseline` band's bracketed `reached` (risk-set) figures in the `sal-v4` table of build `886549a3ac32bdba039691b6d2ca7dc57bb72561` and pooled strictly prior Terms (2017–2025) weighted by `n`.
2. **Sound cert-worthiness analysis:** Accurately identified the four primary factors driving the grant probability down to `0.004`: (a) the pro se status of the petitioners on a paid petition; (b) the unpublished, nonprecedential Ninth Circuit memorandum disposition; (c) a state-law question concerning California's litigation privilege (Cal. Civ. Code § 47(b)) and its gravamen test alleging conflict with California Supreme Court decisions rather than a federal circuit split, despite the Rule 12(b)(6) and Rule 15 framing; and (d) the docket posture (two respondent waivers, one voluntary brief in opposition without a Court request, and a single distribution).
3. **Input hygiene and claim decomposition:** Properly noted that `cert-reply.txt` was marked `empty_text: true` in the October 15 `documents.json` manifest because it was a scanned filing without a text layer, treating it as unavailable rather than absent. Explained each incremental and conditional claim (`relist-increment` `0.03`, `cvsg-increment` `0.002`, `dissent-from-denial` `0.005`, and `summary-disposition-route` `0.30`).
4. **Comparison to top depth:** While concise and accurate on the main cert-selection factors, `claude-baseline` inspected only the opening of the brief in opposition and targeted grep matches in the petition without reading the appendix opinions directly, missing the additional vehicle defects (such as the unchallenged Government Claims Act and service dismissals of the public actors and the district court's direct discussion of *Kimmel* at App. 33).

## Predicted reasoning (`0.78`)

In `predicted_reasoning.md`, `claude-baseline` made four specific claims:
1. **First-conference denial at the November 6, 2026 conference, with an order-list entry around November 9–10, 2026 and no relist:** Specific and borne out (`actual_disposition: "denied"` on `2026-11-09` with `signals.distribution_count: 1`).
2. **No CVSG:** Borne out (`signals.cvsg_date: null`), grounded in the private-party posture and state-law subject matter under Cal. Civ. Code § 47(b).
3. **No dissent from denial:** Borne out (`noted_dissent_from_denial: false`, `votes: []`).
4. **Conditional scope and route if granted:** Unresolved because certiorari was denied.

Every testable claim on the realized path was borne out, including the exact conference and November 9–10, 2026 order-list window. As with `codex-baseline`, because a first-conference denial without CVSG or dissent is strongly favored by the pre-decision posture of a pro se state-law petition, the forecast sits at `0.78`.

## Leakage assessment

- **Mode:** `forward` (predicted `2026-10-15`, resolved `2026-11-09`).
- **Assessment:** `retrieved_outcome_material = false`, `influenced_prediction = "not_applicable"`, `leakage_suspected = false`. All 6 tool calls in `retrieval_log.json` are captured (`result_capture_coverage: 1.0`) and show only local reads of the prompt, schemas, statpack, and provisioned case files while the petition was still pending.
