# Evaluation of gemini-baseline — scotus/73281633, evt-petition-disposition

**Cell:** cert stage, forward mode. **Outcome:** petition DENIED on 2026-10-05 after a single distribution (Conference of 9/28/2026), no CVSG, no relist, no noted dissent (`actual_granted` = 0).

## Scores

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.12 − 0)² = 0.0144.
- `segment_base_rate` = 0.0512, basis `risk_set`. The prediction froze `band: baseline` under `salience_version: sal-v4`, matching the heading of the committed statpack's "Segment base rate by salience band (sal-v4)" table, so the bracketed `reached` figure applies, pooled resolved-weighted over the rendered Terms strictly before OT2025 (2017–2024): 593 / 11,580 ≈ 5.12%. The caption renders 10 of 10 Terms, so no lookback divergence.
- `brier_skill_score` = 1 − 0.0144 / 0.0512² = −4.49. The most negative of the three: this candidate carried the largest uplift above the baseline on a petition that was denied.
- No `vote_accuracy`, no `semantic_grades`: cert stage.

## Reasoning quality: 0.35

The direction and the anchor are right: ~5% for a baseline paid petition, modest absolute number, denial predicted. Beyond that the document is a single paragraph and the analysis is thin in ways that matter.

- **It never engages the briefs.** The captured call list shows reads of the questions presented, the snapshot, the document manifest, and the statpack, and no read of `petition.txt` or `brief-in-opposition.txt` (every row is uncaptured, so I grade on the queries, and no query names either file). The "clean, well-developed circuit split" is therefore the petition's own framing taken from the QP, with no test against the BIO's answer that the circuits apply the same Edenfield rule to different records. The Second Circuit opinion in the appendix cites studies and considers the ingredients-based alternative; a reader who checked would have discounted the split, as the other two candidates did.
- **The strongest reason for denial is absent.** The petition seeks review of an affirmed preliminary-injunction denial while the case proceeds to discovery, and the Second Circuit affirmed on an independent public-interest ground (Pet. App. 30a) that the BIO argues makes the questions non-outcome-determinative. Neither the interlocutory posture nor the alternative ground appears anywhere in the rationale. The outcome turned on exactly those features.
- **Amicus support is read as "high vehicle quality."** Four cert-stage amici are a real grant correlate and the uplift for them is reasonable, but amicus interest says nothing about vehicle quality, and the vehicle here is poor. The two are conflated.
- **The terminal relist bucket is misread.** "The base rate for bucket 0 (no relists yet) is very low" treats the relist-count cut's terminal `0` bucket as the rate a live single-distribution petition faces; the statpack caption says the opposite (that bucket is the rate among petitions that *ended* undistributed-again). The number it reaches is still sensible, but the stated reason is the mistake the pack warns against.
- Minor: the circuit list ("2nd vs. 4th, 5th, 6th, 9th, 10th") does not match the petition's own framing, which places the First and Second Circuits on one side and names the Fourth, Sixth, Ninth and Tenth on the other.

The score reflects a correct, calibrated-enough headline reached on a shallow basis: right answer, little of the work that would have made it robust.

## Big case

My own read is 0.38 (see `evaluation.json`); the predictor's score was in the staged `prediction.json`, so I had seen it before writing mine, and my read is formed on the record and outcome rather than on it. gemini-baseline's 0.65 is the highest of the three and reads the case as "high-profile"; a petition denied at the Long Conference with no writing and no relist is not that, though the doctrinal reach the rationale names is real.

## Leakage

Forward cell, `influenced_prediction` = `not_applicable`, `leakage_suspected` = false. Prediction created 2026-09-16; denial 2026-10-05. The log carries 22 calls with every result unobserved (capture coverage 0.0, an engine's standing shape, not a defect), so I graded on the queries: provisioned-record and statpack reads, one corpus query bounded by `--decided-before 2026-09-15` on topic terms, and one CourtListener opinion search for Central Hudson circuit-split material. No query names this docket or seeks its disposition; no `data/qp-topics/` read. Nothing in the reasoning presupposes the outcome. No sign that a decided case was provisioned forward.
