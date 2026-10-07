# Evaluation of claude-baseline — Wealthy, Inc. v. Cornelia, No. 25-1329 (evt-petition-disposition)

## Outcome and scores

The event is a **cert** cell (`event.yaml` `stage: cert`, moment `distribution`). The petition was **denied** on the October 5, 2026 order list after a single conference (the 9/28 long conference; the two `DISTRIBUTED for Conference of 9/28/2026` entries are one distribution plus a redistribution after the brief in opposition, and the outcome's `distribution_count` is 1), with no noted dissent or statement. `actual_granted` = 0.

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.08 − 0)² = **0.0064**.
- `segment_base_rate` = **0.0512** on the `risk_set` basis. The prediction froze `band: baseline` under `salience_version: sal-v4`, Term 2025; the statpack's band table heading is sal-v4, so the version resolves. Pooling the bracketed `reached` baseline figures weighted by their `n` over every rendered Term strictly before OT2025 (OT2017–OT2024, eight rows; the caption says the table renders 10 of 10 Terms, so no older Term exists in the pack and the configured ten-Term lookback and the rendered window coincide on the available rows) gives 5.12% over a weighted n of 11,580, computed from the table's rounded percentages.
- `brier_skill_score` = 1 − 0.0064 / 0.0512² = **−1.44**. Negative: on a denial, any probability above the 5.1% baseline scores worse than the baseline, and 0.08 sits above it. Of the three candidates this is the smallest shortfall by a wide margin.

The claims block (relist, CVSG, summary route, dissent) is scored by the harness and not here; the forecast document was read only for context on how the number was formed.

## Reasoning quality: 0.88

What drove the score up:

- **Correct anchor, correctly derived.** It named the sal-v4 baseline risk-set figure, pooled the strictly-prior Terms the table renders (about 5.1%, n 11,580), and explained why the other statpack cuts were less specific. That is exactly the baseline this cell is scored against.
- **It read the late filings.** The provisioned documents stopped at the petition (fetched July 18); the brief in opposition and reply postdate that. It fetched both from the snapshot's own links, and its vehicle analysis rests on them rather than on guesswork.
- **It found the decisive negative signal and weighted it properly.** Both filings report that the Court has denied every anti-SLAPP-in-federal-court petition presented to it, including Gopher Media v. Melone this very Term, from the same circuit, after one conference and without a relist, and that at least one earlier denial followed a call for response. The reasoning recognised that this petition's shape so far (call for response, then conference) matched that pattern and discounted the response-request lift heavily. That is the single best piece of case-specific analysis among the three candidates, and the outcome bore it out.
- **A full vehicle inventory**: forfeiture / first-view problem (the panel never passed on the displacement question), unpublished memorandum disposition, interlocutory and possibly non-outcome-determinative posture (pending Lanham Act fee motion, remanded claims), fact-bound Question 2, and the percolation option left open by another Ninth Circuit panel reserving the Berk/Newsham question.
- **Honest uncertainty accounting**: it says the response-request lift is judgment with no published conditional rate, that the CourtListener search was throttled, and that the corpus queries returned nothing relevant.

What held it back:

- The response-request adjustment ("roughly doubling to tripling the band rate") is asserted without any source, then mostly reversed by the denial-history discount; the net 0.08 is reasonable but the intermediate arithmetic is more rhetorical than evidential.
- The final number still sat above the band rate on a petition whose own analysis identified a same-Term, same-circuit, same-question denial and a serious preservation defect. A reader of this document could fairly have landed at or below the baseline.
- A small stale remark: it says the event has no `stage` field; the committed `event.yaml` carries `stage: cert`. Immaterial to the result since the cert default governs either way.

## Leakage

Mode `forward`; the prediction was created September 17, 2026 and the petition was decided October 5, 2026, so the case was genuinely open. The captured log (coverage 1.0) shows the two supremecourt.gov PDF fetches (filings dated Aug 26 and Sep 11), one throttled CourtListener search, and two unrelated corpus queries. No `retrieved_doc_date` on or after the resolution, no query for this petition's result, no `data/qp-topics/` read, and the reasoning treats the docket as still distributed throughout. `retrieved_outcome_material` = false, `influenced_prediction` = not_applicable, `leakage_suspected` = false. Not a mis-provisioned decided case. The candidate's `flags.json` is not staged, so its absence from my view is not evidence either way; the finding rests on the log and the prose.

## Big-case read

My independent read is 0.35 (see `evaluation.json`): an important, recurring procedural question carried by a small, low-profile vehicle that was denied without comment.
