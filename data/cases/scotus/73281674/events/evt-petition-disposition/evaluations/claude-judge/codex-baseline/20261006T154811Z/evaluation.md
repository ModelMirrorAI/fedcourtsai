# Evaluation of codex-baseline — PG Publishing Co. v. NLRB, No. 25-1192 (cert stage)

## Outcome and scores

The petition was **denied on October 5, 2026** in the orders following the September 28 long conference: one distribution, no relist, no CVSG, no noted dissent (`outcome.json`: `actual_disposition` denied, `actual_granted` 0, `distribution_count` 1). The event's stage is `cert`, so the cert rules govern.

- `predicted_disposition` denied vs actual denied → **correct = 1**.
- `probability` 0.035 → **brier_score = 0.001225**.
- **segment_base_rate = 0.0512** (`base_rate_basis` = `risk_set`). The prediction's frozen context carries `band` = `baseline` and `salience_version` = `sal-v4`, and the statpack's per-Term band table is headed sal-v4, so the risk-set path applies. Pooled the bracketed `reached` figure for `baseline` over Terms 2017–2024 (every rendered Term strictly before the case's Term 2025; the caption shows 10 of 10 Terms, so the rendered window is the pack's whole window and the in-code ten-Term lookback reaches the same rows): 593 / 11580 = 0.05121 from the unrounded `prefix_est_grant_rate` × `prefix_weighted_resolved` in `metrics/statpack.json`.
- **brier_skill_score ≈ 0.533** = 1 − 0.001225 / (0.05121 − 0)².
- No `vote_accuracy` (cert cell; the noted votes are elicited, never scored). The `claims` block and `predicted_reasoning.md` are not scored here.

## Reasoning quality: 0.85

What drove the score:

- **The anchor is right and the method is right.** The candidate pooled the bracketed reached figure, not the terminal one, over the strictly-prior rendered Terms, and computed it from the unrounded pack (593/11580 — the same number I get). It expressly declined to use the terminal relist-0 and CVSG-none buckets as forward hazards, which is the correct reading of those cuts: they condition on a terminal state that is downstream of the outcome.
- **The vehicle analysis tracks the record.** It read the provisioned union opposition and fetched the federal respondent's June 17 opposition (a docketed, pre-cutoff filing the provisioning omitted), and its treatment of each QP matches what those briefs say: the independent premature-impasse finding that supports the only live remedy; the SG's point that the panel stated plenary legal review so the Loper Bright framing has no concrete instance to attach to; the §10(e) forfeiture of the Thryv question; the Macy's denial on June 15 and the SG's express refusal to seek a remand here. The Macy's denial is used modestly and only to discount a hold, which is the right weight.
- **Epistemic hygiene.** It separates what it verified from what it took on the parties' word (the appendix and the reply were not read), says the adjustment is judgmental rather than fitted, and does not count overlapping vehicle defects as independent evidence.

What held it back:

- **The discount is small relative to its own findings.** Having identified an SG opposition that disputes the split, an unpublished opinion below, an independent alternative ground, a forfeited third question, a just-denied cleaner vehicle on that question, and no amicus support, it moved only from 5.1% to 3.5%. The analysis supports a larger move than the number reflects; the soundness is in the analysis, the calibration is cautious.
- The 12% further-distribution figure is asserted rather than reasoned from anything in the pack, as the candidate itself concedes.

## Leakage

`mode` = `forward`. The prediction was created September 16, 2026 against the September 15 snapshot and the petition was decided October 5, so the case was genuinely open: this is not a mis-provisioned forward cell. The staged log holds 34 calls, 32 captured and 2 `unobserved` web-search rows, which I graded on their queries: one is the URL of the federal opposition PDF, the other a supremecourt.gov search for *Loper Bright* and docket 22-451 — neither asks about this petition's disposition. The captured calls read the prompt, schemas, provisioned record and statpack, and fetched the same June 17 opposition in memory; no `retrieved_doc_date` is at or after the resolution, no call queries this docket's later history, and nothing under `data/qp-topics/` was read. The reasoning expressly disclaims knowing the outcome and treats the stay-application denial and the Macy's denial as what they are, pre-petition history and a different docket. `retrieved_outcome_material` = false, `influenced_prediction` = `not_applicable`, `leakage_suspected` = false. (The candidate's own `flags.json` is not staged, so its disclosures reached me only through `reasoning.md` and `retrieval.md`, where it made them.)

## Big case (my independent read): 0.30

A private employer's petition from an unpublished, non-precedential Third Circuit affirmance of an NLRB bad-faith-bargaining order. The third question (Thryv consequential damages) is a live national issue with a real circuit split, but it was held forfeited below, so this vehicle could not carry it; the first question is fact-bound and the second relabels substantial-evidence review. The paper was sold in May 2026, leaving only make-whole relief at stake; the SG opposed; no amici filed; denied without noted dissent at the first conference. Stakes beyond the parties were modest.
