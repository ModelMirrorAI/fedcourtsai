# Evaluation of claude-baseline — scotus/9026000173, evt-petition-disposition

## Outcome and scores

The event is a **cert** cell (`stage: cert`, moment `distribution`). The Court denied the petition on October 5, 2026 (`actual_disposition: denied`, `actual_granted: 0`), with no noted dissent, after one distribution of the petition itself (August 26 for the September 28 long conference; the May 19 distribution was of the linked fee motion, denied June 8).

- `correct` = 1: the candidate predicted `denied`, exact label match.
- `brier_score` = (0.005 − 0)² = 0.000025.
- `segment_base_rate` = 0.169, basis `risk_set`. The prediction's frozen context carries `band: elevated` **and** `salience_version: sal-v4`, matching the heading of the committed `metrics/statpack.md` table "Segment base rate by salience band (sal-v4)", so the bracketed `reached` figures apply, pooled resolved-weighted over every rendered Term strictly before Term 2026 (OT2017–OT2025, weighted n = 3,085): 521.5 / 3,085 = 0.1690. The pack renders 10 of 10 Terms, so no lookback divergence arises.
- `brier_skill_score` = 1 − 0.000025 / 0.169² = 0.9991.
- `vote_accuracy` omitted (cert stage).
- `claim_scores` and `process_version` left to the harness.

## Reasoning quality: 0.87

What drove the score. The rationale anchors correctly (pooled bracketed elevated reached rate ≈ 17% over OT2017–OT2025, nine Terms, weighted denominator ≈ 3,085) and then gives the clearest account of why the anchor overstates this petition's chances. Its central observation is right and well evidenced from the snapshot: the two `DISTRIBUTED` entries belong to two different filings, the May 19 one to the motion for leave to proceed as a veteran (linked docket 25M81, denied June 8) and the August 26 one to the petition's own first distribution, so the petition was a relist-0 paid petition at its first conference rather than a twice-considered one. It draws the correct inference that the band rests on an inflated distribution count, says it is scored against the band anyway, and forecasts from the true posture. The remaining factors are each apt: the Solicitor General's waiver on a petition against the United States, the pro se petitioner, the unpublished affirmance, the petition's reliance on the Fourth Circuit's own precedent (making the ask error-correction rather than split resolution), the mis-described authorities (State Farm v. Campbell, Loper Bright), and the neutral originating-circuit cut. It candidly reports that the Fourth Circuit opinion was not retrievable and that the one corpus query returned nothing analogous, and it states each secondary probability as the conditional the contract asks for.

Where it falls short. A few characterizations are stated more confidently than the evidence allows: that "pro se filings sit well below" the baseline band's rate is asserted without a figure, and the claim that the band was produced by the distribution miscount is inferred rather than verified against the scorer. Neither affects the soundness of the conclusion. The write-up also leans on the forecast of the exact order-list date, which belongs to the forecast document and is not scored here.

## Leakage

Forward cell. See `leakage.notes` in `evaluation.json`: every call is captured; the single corpus query's newest `retrieved_doc_date` is 2026-09-10, before resolution, and its rows were unrelated grants; the two CourtListener searches sought the Fourth Circuit opinion below and returned nothing, and neither touches this petition's Supreme Court disposition. `retrieved_outcome_material: false`, `influenced_prediction: not_applicable`, `leakage_suspected: false`. The case was genuinely open on September 18, so the forward provisioning was correct.

## Big case

My independent read, formed before weighing the candidate's: 0.05. One former employee's installation debarment, pro se, unpublished below, SG waived, denied without comment; the record-rule exceptions question matters in the abstract but this petition was not its vehicle. (The candidate's 0.06 is recorded for the panel's rank-agreement, not graded here.)
