# Evaluation of gemini-baseline — PG Publishing Co. v. NLRB, No. 25-1192 (cert stage)

## Outcome and scores

The petition was **denied on October 5, 2026** in the orders following the September 28 long conference: one distribution, no relist, no CVSG, no noted dissent (`outcome.json`: `actual_disposition` denied, `actual_granted` 0, `distribution_count` 1). The event's stage is `cert`, so the cert rules govern.

- `predicted_disposition` denied vs actual denied → **correct = 1**.
- `probability` 0.015 → **brier_score = 0.000225**.
- **segment_base_rate = 0.0512** (`base_rate_basis` = `risk_set`). The prediction's frozen context carries `band` = `baseline` and `salience_version` = `sal-v4`, matching the statpack table's heading, so the risk-set path applies. Pooled the bracketed `reached` figure for `baseline` over Terms 2017–2024 (all rendered Terms strictly before Term 2025; the caption shows 10 of 10 Terms, so the rendered window is the pack's whole window and coincides with the in-code ten-Term lookback): 593 / 11580 = 0.05121 from the unrounded figures in `metrics/statpack.json`.
- **brier_skill_score ≈ 0.914** = 1 − 0.000225 / (0.05121 − 0)².
- No `vote_accuracy` (cert cell). The `claims` block and `predicted_reasoning.md` are not scored here.

## Reasoning quality: 0.45

The best Brier of the three came from the thinnest analysis, and `reasoning_quality` grades the soundness of the path rather than the result.

What is sound:

- The direction is right and the stated reasons are real: the union opposition does press an independent premature-impasse ground, does argue the second question is a complaint about factual review rather than statutory interpretation, and there were no amici. Each of those is in the provisioned brief, and each is a legitimate reason to sit below the band rate.
- The CVSG and summary-disposition judgments are correctly reasoned (the federal government is already a respondent; there is no intervening decision to ground a GVR).

What held it back:

- **The anchor is mis-specified.** The candidate notes the ~5% risk-set rate and then anchors on the terminal relist-0 bucket's 1.2% as if it were the forward hazard for a petition at its first distribution. That bucket is conditioned on never having been relisted, a terminal state that is largely downstream of the outcome (grants mostly follow relists), so it is not the rate a live petition at distribution one faces; the statpack's scope line and the predict contract both say the terminal cuts are not forward transition probabilities. The 1.5% number is therefore reached mostly by conditioning on a future the petition had not yet had, not by analysis of this petition. That it landed close to the realized outcome does not make the route sound.
- **The record was only partly engaged.** The log shows targeted greps of a few headings in the union opposition and the petition's first argument heading; the first question's claimed D.C. and Ninth Circuit conflict is never addressed, the third question's §10(e) forfeiture and the Macy's denial are not mentioned, and the federal respondent's opposition on the docket was neither fetched nor noted. The one-paragraph rationale does not say how much weight each factor carried.
- No uncertainty statement, no range, and no account of what would move the number.

## Leakage

`mode` = `forward`. Created September 16, 2026 against the September 15 snapshot; decided October 5. Genuinely open at prediction, so not a mis-provisioned forward cell. The staged log holds 28 calls, every one `unobserved` (`result_capture_coverage` 0.0 — the engine's standing telemetry shape, not a defect), so each was graded on its query: reads of the prompt, `AGENTS.md`, the provisioned context, snapshot, document manifest, questions presented, two statpack sections, and grep slices of the two provisioned briefs; then the output writes and a validate run. No web, MCP, or corpus call; no query names this docket's later history or the disposing order; nothing under `data/qp-topics/` was read. `retrieved_outcome_material` = false, `influenced_prediction` = `not_applicable`, `leakage_suspected` = false. With every result unobserved, the `false` rests on the queries alone, which is the most the log supports; nothing in the reasoning presupposes the outcome.

## Big case (my independent read): 0.30

A private employer's petition from an unpublished, non-precedential Third Circuit affirmance of an NLRB bad-faith-bargaining order. The third question (Thryv consequential damages) is a live national issue with a real circuit split, but it was held forfeited below, so this vehicle could not carry it; the first question is fact-bound and the second relabels substantial-evidence review. The paper was sold in May 2026, leaving only make-whole relief at stake; the SG opposed; no amici filed; denied without noted dissent at the first conference. Stakes beyond the parties were modest.
