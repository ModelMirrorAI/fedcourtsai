# Evaluation: codex-baseline — Scroggins v. City of Shreveport, No. 26-80 (cert, petition disposition)

## Outcome and scores

The event is a **cert**-stage petition disposition. `outcome.json` records `denied` on 2026-10-05 (first order list of OT2026, after the September 28, 2026 long conference), `actual_granted` = 0, one distribution, no CVSG, no noted dissent from denial.

- `correct` = 1: `predicted_disposition` `denied` matches `actual_disposition` `denied` exactly.
- `brier_score` = (0.015 − 0)² = 0.000225.
- `segment_base_rate` = 0.0502, `base_rate_basis` = `risk_set`. The prediction's frozen context carries both `band: baseline` and `salience_version: sal-v4`, matching the statpack's "Segment base rate by salience band (sal-v4)" heading. Pooling the bracketed `reached` figure resolved-weighted over every rendered Term strictly before Term 2026 (OT2017–OT2025) gives 638 / 12,720 = 0.05016, from the per-Term `prefix_est_grant_rate` × `prefix_weighted_resolved` fields in `metrics/statpack.json`. The caption says "Most recent 10 of 10 Term(s)", so the rendered window is the pack's whole window; no lookback divergence to flag.
- `brier_skill_score` = 1 − 0.000225 / (0.0502)² = 0.911.
- `vote_accuracy` omitted (cert stage; never scored). `judgment_correct` null. No `semantic_grades` on a cert event. `claim_scores` left to the harness.

## Reasoning quality: 0.78

A careful, well-bounded analysis that was right, but one that stopped short of the evidence it could have had.

Strengths:

- **Exactly the right anchor.** It pooled the sal-v4 baseline risk-set figure from the statpack JSON over OT2017–OT2025, reported 638 / 12,720 = 5.016%, said which fields it used and why (bracketed `reached`, not terminal, not the unresolved current Term), and even recorded the statpack's commit vintage while correctly declining to call that a corpus-freshness measurement. This is the most precise anchor of the three.
- **Disciplined information boundary.** It said plainly what it read, what it did not (appendix, lower opinions, no BIO), and that the petitioner's characterisations of the dissent were representations, not verified facts. It refused to treat the response waiver as a concession.
- **Reasonable adjustments.** Error-correction framing, no split, thin evidentiary account, and the forfeiture issue as a "possible vehicle complication" are all the right considerations, each weighted modestly rather than decisively.

What cost it:

- **It did not read the decision under review, and that was available.** The Fifth Circuit opinion was published on CourtListener in October 2025, well before the petition. Reading it would have shown that forfeiture was the ground of decision, not a complication, and that the panel found apparent fabricated citations in the appellate brief. The candidate recognised the gap ("the supplied material does not establish which arguments were preserved") but left it as uncertainty instead of resolving it with a pre-decision source the tools offered. Its 1.5% is therefore a hedge against vehicle facts it could have known, and it is three to fifteen times its peers' numbers for that reason.
- **Over-caution on legitimate forward signal.** It declined to draw anything from the snapshot's silence after the September 28 conference. That silence is provisioned input, and the Court's customary pre-order-list release of long-conference grants makes it mild, legitimate evidence of denial; treating it as unusable is a defensible but suboptimal choice.
- **"Pro se status itself is not a merits defect"** is true as a legal matter but understates an empirical regularity the cert forecast turns on: paid pro se petitions are granted far less often than the band's counseled population. Declining to weight it is a mild analytic miss.
- The two hosted web calls for Rule 10 returned nothing usable; the candidate said so honestly and claimed nothing from them.

## Leakage: none; forward cell

`retrieval_log.json` records `mode: forward`, `result_capture_coverage` 0.92, 25 calls. The prediction was created 2026-10-04T20:48Z on the 2026-10-04 snapshot; the denial was entered 2026-10-05. No call carries a `retrieved_doc_date`; the only external calls are two `web-search` rows marked `unobserved`, which I graded on their queries as the marker rule requires: one is a Rule 10 phrase search, the other the Cornell LII Rule 10 page. Neither names this case, its parties, or its docket number. All other calls are provisioned-input reads, statpack reads, schema reads, a git log on the statpack, and the output write. Nothing touched `data/qp-topics/`. `retrieval.md` matches the log. `retrieved_outcome_material` = false, `influenced_prediction` = `not_applicable`, `leakage_suspected` = false.

## Big case

My independent read is 0.03, formed before looking at the predictor's score: a single pro se Title VII promotion dispute, affirmed on forfeiture, no split, no amicus, denied without a noted dissent. The candidate's 0.22 rests on the recurring importance of the summary-judgment and pro se topics in general; the panel will rank it, but on my reading that is the importance of the subject, not of this case.
