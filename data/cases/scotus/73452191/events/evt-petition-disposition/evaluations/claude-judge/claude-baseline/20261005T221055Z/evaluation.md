# Evaluation of claude-baseline — scotus/73452191, evt-petition-disposition

## Outcome and scores

Cert-stage cell, forward mode. The petition (No. 25-1356, Bernard v. Ignelzi) was distributed once, for the September 28, 2026 conference, and **denied on October 5, 2026** with no noted dissent. `actual_disposition` = `denied`, `actual_granted` = 0.

- `correct` = 1: the candidate predicted `denied`.
- `brier_score` = 0.025² = 0.000625.
- `segment_base_rate` = 0.0512 on the `risk_set` basis. The prediction froze `band: baseline` under `salience_version: sal-v4`, matching the statpack band table's heading, so the bracketed `reached` figure applies, pooled resolved-weighted over the rendered Terms strictly before Term 2025 (OT2017 through OT2024, eight rows, n = 11,580). The table renders all 10 Terms the pack holds, so the rendered window and the configured ten-Term lookback reach the same rows; no divergence to flag.
- `brier_skill_score` = 1 − 0.000625 / 0.0512² = 0.762. Lowest of the three because its probability was the highest, but all three sit in the same well-calibrated region for a first-conference denial.
- `vote_accuracy` omitted (cert cell). `judgment_correct` null. No `semantic_grades` block.

## Reasoning quality: 0.85

What is sound:

- Correct anchor, shown in full: the eight sal-v4 baseline reached rows, pooled to 5.1% over n = 11,580, with the version match checked explicitly, and the whole-segment cuts used only as a shape check.
- The six downward adjustments are the right ones and are ranked sensibly. Forfeiture is correctly named the single largest discount, with the petition's own quotations of the decision below cited. The unpublished, non-precedential status of the decision below is noted and its effect on the "three States without a remedy" framing explained. The split is read as softer than pleaded for the right reason: Gibson and Rockett involve personal participation, this judge directed deputies in a pending matter, and Mireles v. Waco is the closer authority. The waiver and the Court's silence before distribution are read as concordant signals. The plaintiff-side skew of immunity grants and summary reversals is a real and relevant pattern.
- Verified the comparator cases exist on CourtListener (Gibson v. Goldston, CA4 2023; Rockett v. Eighmy, CA8 2023) rather than taking the petition's word.
- The relist probability is derived from the table itself (the elevated-reached over baseline-reached ratio as a population rate of ever moving up, then discounted for this docket), which is a grounded way to set that claim rather than a guess.
- An honest uncertainty section: it has not read the Third Circuit opinion, flags a from-memory belief about Gibson's cert history as unverified and immaterial to the number, and gives a range (0.015 to 0.04) around the point estimate.

Minor weaknesses:

- The "petition quality" adjustment (drafting errors, rhetorical passages, a "disgruntled-litigant filing") is a legitimate cert-stage heuristic but is the least disciplined of the six and shades toward characterizing the litigant rather than the vehicle.
- It reports the event file as carrying no `stage` or `moment` field; the event file in this cell carries both. Whether the file was later backfilled I cannot tell, and the candidate reached the right stage reading either way, so this is noted rather than penalized.
- Given that it correctly identified the Court will not grant without a response and that none was called for before distribution, 0.025 is slightly generous to the grant side relative to its own analysis; the candidate's lower bound of 0.015 would have fit its reasoning better.

Net: the most complete legal analysis of the three, with verified comparators and honest uncertainty. Scored level with codex-baseline: it is broader where codex-baseline is more careful about what is allegation versus finding.

## Leakage: not applicable

Forward cell; the prediction was created September 16, 2026, before the conference and the denial. The log (28 calls, capture coverage 1.0) shows one corpus query over granted SCOTUS rows and six CourtListener searches: two on this case's caption returned zero results (the decision below is unpublished and unindexed), one timed out, and the rest located Gibson v. Goldston (`retrieved_doc_date` 2023-10-30) and Rockett v. Eighmy (2023-06-22), both pre-event comparators. No `retrieved_doc_date` falls on or after resolution, no web search, no `data/qp-topics/` read. Two `file-read` calls on the engine's own persisted tool-output files are the engine re-reading its own results. `retrieved_outcome_material` = false, `influenced_prediction` = `not_applicable`, `leakage_suspected` = false.

## Big case: 0.15

Formed from the record: a doctrinally interesting but narrow judicial-immunity question, a single landlord-tenant contempt dispute, an unpublished forfeiture-based decision below, a waiver, and a first-conference denial with no writing. Legal-press interest at most. The staged prediction.json exposes each candidate's `big_case_score`, so the three scores were visible before this read was fixed; the read rests on the record, not on them.
