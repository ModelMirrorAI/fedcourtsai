# Evaluation of gemini-baseline — scotus/73281703, evt-petition-disposition

**Stage:** cert (event.yaml `stage: cert`). **Outcome:** petition denied 2026-10-05 after the 2026-09-28 conference, `actual_granted` 0, no noted dissent, two distributions, no CVSG.

## Scores

| field | value |
| --- | --- |
| predicted_disposition | denied (matches) → `correct` 1 |
| probability | 0.11 → `brier_score` 0.0121 |
| segment_base_rate | 0.1724 (`risk_set`) |
| brier_skill_score | 0.593 |
| reasoning_quality | 0.55 |

**Base rate.** The prediction froze `band: elevated` with `salience_version: sal-v4` and the statpack's segment table heading is also sal-v4, so the basis is `risk_set`. I pooled the bracketed `reached` figure for `elevated` over the eight Term rows strictly before Term 2025 that the table renders (2017–2024; caption says 10 of 10 pack Terms are rendered, so the rendered window is the pack's window and there is no lookback divergence to flag): weighted n 2810, rate 0.1724. The baseline Brier is 0.0297, which this candidate's 0.11 beats clearly.

## What the prediction got right

The categorical call (denied) and the direction of the adjustment below the band anchor were right, and the two conditional forecasts in the forecast document (no further relist, no separate writing) both came true. The candidate correctly read the `distribution_count` of 2 as administrative: the first distribution preceded the call for a response, so the Long Conference was the petition's first real consideration.

## Where the reasoning is weaker

The rationale is a single paragraph. Its anchor ("approximately 17.5%") is one Term row of the table rather than the pooled prior-Term rate; the difference is immaterial here (17.5 vs 17.2) but the method is not the one the table caption asks for. The vehicle objection is described loosely — "the final judgment did not turn on the question presented, suggesting alternative state-law grounds" — whereas the brief in opposition's actual argument is that this is a retaliation claim by a staffing-agency employee who was not the district's independent contractor, so the question presented does not describe the case; the retrieval log shows the candidate read only the first 150 lines of the petition and of the opposition, which is consistent with that imprecision. The acknowledged split, the state-court origin, the lack of amici, and the small verdict are not weighed individually. The reasoning reached the right place with a correct core insight (vehicle mismatch dominates), but on a thin reading and without engaging the substance of the split, which is what holds `reasoning_quality` at 0.55.

## Leakage

Forward cell; `influenced_prediction` is `not_applicable`, `retrieved_outcome_material` false, `leakage_suspected` false. The prediction was created 2026-09-18, before the conference and the denial. The log carries 28 calls, all reads of the provisioned record, the prompt, AGENTS.md, and the statpack, plus the candidate's own writes and validate runs; no web, MCP, or corpus calls. Every call is `unobserved` (coverage 0.0 — the engine's standing capture shape, not a defect), so I graded on queries: none names this case's disposition or a post-resolution document. Nothing suggests the decided case was mis-provisioned forward: the snapshot read was dated 2026-09-17.

## Big case

My independent read, formed before looking at the candidate's score: 0.30 — a real inter-court division on section 504's reach to non-employees, but a weak vehicle (small general verdict, retaliation by a non-contractor, state-court origin, no amici) and a plain denial. The candidate's 0.40 is recorded in its prediction; I supply only my read.

## Harness fields

`claim_scores`, `process_version`, `base_rate_salience_version`, and `prediction_run_id` are left to the harness. `vote_accuracy` and `judgment_correct` are omitted/null on this cert cell. No `semantic_grades` block: a cert event declares no semantic set.
