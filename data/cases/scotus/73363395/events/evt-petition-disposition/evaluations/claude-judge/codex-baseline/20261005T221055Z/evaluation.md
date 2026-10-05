# Evaluation — codex-baseline

**Cell.** Cert-stage, forward-mode petition cell for Campo v. Uber Technologies, No. 25-1292 (Florida Third DCA). The outcome is a denial on the October 5, 2026 order list after the September 28 long conference, with one distribution, no CVSG and no noted dissent (`outcome.json`: `actual_disposition: denied`, `actual_granted: 0`, `distribution_count: 1`).

## Quantitative

- `correct = 1`: predicted `denied`, actual `denied`.
- `brier_score = 0.000025`: probability 0.005 against 0.
- `segment_base_rate = 0.051209`, `base_rate_basis = risk_set`. The prediction's frozen context carries `band: baseline` and `salience_version: sal-v4`, and the committed statpack's segment table heading is `sal-v4`, so the risk-set basis applies. I pooled the bracketed `reached` figure for `baseline`, resolved-weighted, over every rendered Term strictly before this case's Term 2025: 2017–2024, eight Terms, 593 grants over a weighted n of 11,580 (full-precision rates from `metrics/statpack.json`; the rendered rounded percentages give 0.051203, the same number to four places). The caption renders 10 of 10 Terms, so the rendered window is the whole pack and matches the in-code 10-Term lookback. No divergence to flag.
- `brier_skill_score = 0.990467`: 1 − 0.000025 / (0.051209 − 0)².
- No `vote_accuracy` (cert stage; none predicted in any case). No `judgment_correct` (no judgment on either side).

## Reasoning quality: 0.85

What drove the score:

- **Right anchor, correctly pooled.** The candidate used the sal-v4 baseline bracketed `reached` figure, pooled 2017–2024 from full-precision JSON (593/11,580 = 5.12%), explicitly excluded the case's own Term, and explained why the risk-set population rather than the terminal rate is the one a live petition faces. This matches my own computation exactly.
- **The legal core is right.** It identified the dispositive problem: both questions presented rest on the Seventh Amendment, which does not bind the States, and it retrieved and correctly characterized Walker v. Sauvinet, 92 U.S. 90 (1876), rather than asserting the point. It also noticed the petition's own Florida authority conceding the federal-court limitation (I confirmed the petition reproduces that language at its pages 42 and 44), and that the due-process question is not separated from an evidentiary-sufficiency grievance.
- **Careful docket reading.** It correctly treated the April distribution and May grant of motion 25M75 (sealed supplemental appendix) as not a relist, preserved the distribution count of one, read the June 10 waiver as a waiver rather than an extraction failure, and read the September 28 distribution as a first consideration. All of this is borne out by the resolved docket.
- **Disciplined use of the cuts.** It stated that the relist-bucket and CVSG rates are terminal descriptive buckets, not forward transition probabilities, and did not derive its claim probabilities mechanically from them. That is the right reading of the statpack and a point the thinner candidate in this cell missed.
- **Honest about limits.** It said it had not read the lower-court opinions or appendix, that its web searches returned nothing usable, and that the tenfold reduction from the anchor is judgmental.

What held it back from higher: it did not read the Third DCA opinion, which was one CourtListener call away and would have shown that no federal question was pressed or passed upon below, the sharpest single reason this petition could not be granted. The document is also long for what it establishes. Neither is an error.

## Leakage

Mode `forward` per the staged log. The cell ran on September 16, 2026 against a snapshot of the same date; the petition was then distributed for a conference still twelve days away, and the denial came October 5. The log shows 33 calls: local reads of the prompt, schema, snapshot, petition and statpack; three `web-search` rows (all `unobserved`, so graded on their queries, which are general Rule 10 and Seventh Amendment searches naming nothing about this case); and three CourtListener calls that located and read Walker v. Sauvinet (1876). No call queried this docket or caption, no `retrieved_doc_date` is on or after October 5, 2026, and the reasoning forecasts the denial as a future event. The case was genuinely open, so the forward default stands: `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, `leakage_suspected = false`.

## Big case (my independent read): 0.06

A single wrongful-death vicarious-liability suit that lost on summary judgment in Florida, brought to the Court on a Seventh Amendment theory that does not apply to state courts, denied at the first conference without a response or any writing. Rideshare liability is a live policy area, but this petition presents no legal question about it, and the denial changes nothing beyond these parties. Disclosure: the candidate's `big_case_score` is a field of the staged `prediction.json`, which I had read for the probability before forming this read; I set my number from the record and outcome rather than from that field, but the reader should know the order.
