# Evaluation of claude-baseline — PG Publishing Co. v. NLRB, No. 25-1192 (cert stage)

## Outcome and scores

The petition was **denied on October 5, 2026** in the orders following the September 28 long conference: one distribution, no relist, no CVSG, no noted dissent (`outcome.json`: `actual_disposition` denied, `actual_granted` 0, `distribution_count` 1). The event's stage is `cert`, so the cert rules govern.

- `predicted_disposition` denied vs actual denied → **correct = 1**.
- `probability` 0.022 → **brier_score = 0.000484**.
- **segment_base_rate = 0.0512** (`base_rate_basis` = `risk_set`). The prediction's frozen context carries `band` = `baseline` and `salience_version` = `sal-v4`, matching the statpack table's heading, so the risk-set path applies. Pooled the bracketed `reached` figure for `baseline` over Terms 2017–2024 (all rendered Terms strictly before Term 2025; the caption shows 10 of 10 Terms, so the rendered window is the pack's whole window and coincides with the in-code ten-Term lookback): 593 / 11580 = 0.05121 from the unrounded figures in `metrics/statpack.json`.
- **brier_skill_score ≈ 0.815** = 1 − 0.000484 / (0.05121 − 0)².
- No `vote_accuracy` (cert cell). The `claims` block and `predicted_reasoning.md` are not scored here.

## Reasoning quality: 0.88

What drove the score:

- **Anchor and pooling are shown, and correct.** The eight prior-Term reached rates are tabulated with their `n`, pooled to 593/11580, and the candidate states that this is the figure it will be scored against. The terminal relist-0 and CVSG-none buckets and the ca3 circuit rate are cited as context only and not used as the anchor, which is the right handling.
- **The sharpest substantive analysis of the three.** Each downward factor is tied to something in the record: the SG's argument that the Third Circuit's inference rule is shared by the Seventh, Tenth, Eleventh and D.C. Circuits and that the D.C. Circuit decision the panel relied on is on the same side (the candidate read the petition's own authorities and explains why the SG has the better of it); the Board's "even absent bad faith" impasse finding and the May 2026 sale that leaves only make-whole relief resting on that finding; the second question's collapse into a complaint about the word "deferential," with the SG's Urias-Orellana point; the third question's §10(e) forfeiture, the Third Circuit's own rejection of Thryv in Starbucks, and the June 15 Macy's denial where the government had asked for a GVR; the absence of amici; and the January stay denial without noted dissent. It also pulled recent employer-side NLRB petitions from the corpus (Cemex, NP Red Rock) as denied analogs.
- **The number is argued, not asserted.** It states a range (1.5–3.5%), says what would move it outside the range, and names its weakest claims (the relist-increment, the unseen panel opinion, the unknown Macy's dissent line-up).

What held it back:

- The relist-increment of 0.27 is derived from the terminal bucket share of petitions that ever pick up a second distribution, which the candidate itself flags as the least anchored number; the adjustment above that marginal rate for a long-conference petition is plausible but unreasoned.
- As disclosed, the panel opinion itself was not read; the characterization of its holding rests on the briefs.

## Leakage

`mode` = `forward`. Created September 16, 2026 against the September 15 snapshot; decided October 5. Genuinely open at prediction, so not a mis-provisioned forward cell. The staged log holds 36 calls, all captured (`result_capture_coverage` 1.0): provisioned record and statpack reads; five `fedcourts query` calls over 2020s SCOTUS dispositions (the one legible `retrieved_doc_date`, 2026-05-14, is a corpus row date well before the resolution); three CourtListener searches for Macy's, No. 25-627 — a different docket — which returned nothing; a web fetch of the federal respondent's June 17 opposition, a docketed pre-cutoff filing; and a directory listing of the candidate's own earlier prediction outputs on other cases, used as a format reference, which carries nothing about this petition. No call reaches this docket's post-September history or the disposing order, and nothing under `data/qp-topics/` was read. The reasoning treats the Macy's denial and the stay denial as what they are. `retrieved_outcome_material` = false, `influenced_prediction` = `not_applicable`, `leakage_suspected` = false. The candidate disclosed the un-provisioned fetch in `reasoning.md` and `retrieval.md`; that disclosure is a point for the cell's integrity.

## Big case (my independent read): 0.30

A private employer's petition from an unpublished, non-precedential Third Circuit affirmance of an NLRB bad-faith-bargaining order. The third question (Thryv consequential damages) is a live national issue with a real circuit split, but it was held forfeited below, so this vehicle could not carry it; the first question is fact-bound and the second relabels substantial-evidence review. The paper was sold in May 2026, leaving only make-whole relief at stake; the SG opposed; no amici filed; denied without noted dissent at the first conference. Stakes beyond the parties were modest.
