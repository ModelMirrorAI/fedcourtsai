# Evaluation of gemini-baseline — scotus/9026000173, evt-petition-disposition

## Outcome and scores

The event is a **cert** cell (`stage: cert`, moment `distribution`). The Court denied the petition on October 5, 2026 (`actual_disposition: denied`, `actual_granted: 0`), with no noted dissent, after one distribution of the petition itself (August 26 for the September 28 long conference; the May 19 distribution was of the linked fee motion, denied June 8).

- `correct` = 1: the candidate predicted `denied`, exact label match.
- `brier_score` = (0.005 − 0)² = 0.000025.
- `segment_base_rate` = 0.169, basis `risk_set`. The prediction's frozen context carries `band: elevated` **and** `salience_version: sal-v4`, matching the heading of the committed `metrics/statpack.md` table "Segment base rate by salience band (sal-v4)", so the bracketed `reached` figures apply, pooled resolved-weighted over every rendered Term strictly before Term 2026 (OT2017–OT2025, weighted n = 3,085): 521.5 / 3,085 = 0.1690. The pack renders 10 of 10 Terms, so no lookback divergence arises.
- `brier_skill_score` = 1 − 0.000025 / 0.169² = 0.9991.
- `vote_accuracy` omitted (cert stage).
- `claim_scores` and `process_version` left to the harness.

## Reasoning quality: 0.55

What drove the score. The rationale is short but its load-bearing points are correct: the petitioner is self-represented on a paid docket; the Solicitor General waived, and the Court does not grant a paid petition without first calling for a response; the dispute is an individual installation debarment and a poor vehicle for a record-rule split; a CVSG is impossible with the federal government already a party; and the earlier distribution was of the motion to proceed as a veteran, not the petition. It names the elevated band's prior-Term reached rate (~16%, against the pooled 16.9%) as its anchor and states the adjustment to 0.5% explicitly. The number it reached is well calibrated to the posture.

Where it falls short. The analysis is thin. The candidate's retrieval log shows it read the questions presented but not the petition text, so the vehicle judgment rests on the docket and the QP alone, with no engagement with the asserted split, the cited authorities, or the decision below. One stated reason is wrong: it attributes the elevated band to the federal government being the respondent, whereas under sal-v4 a caption band (`federal`) attaches to a federal *petitioner* and a private petitioner is never in its risk set; the far likelier source of the band is the distribution count of two, which the candidate itself notes was inflated by the motion distribution but does not connect to the band. The relist and dissent probabilities are asserted without reasons. The document is sound as far as it goes, and it goes only a little way.

## Leakage

Forward cell. See `leakage.notes` in `evaluation.json`: every marker-carrying call is `unobserved` (coverage 0.0, the engine's standing shape), so each call is graded on its query. The queries are file reads of provisioned inputs, prompt and instructions, statpack greps, one generic corpus query naming no case, and the output writes. No web or CourtListener call, nothing naming this petition's disposition. `retrieved_outcome_material: false`, `influenced_prediction: not_applicable`, `leakage_suspected: false`. The case was genuinely open on September 18, so the forward provisioning was correct.

## Big case

My independent read, formed before weighing the candidate's: 0.05. One former employee's installation debarment, pro se, unpublished below, SG waived, denied without comment; the record-rule question matters in the abstract but this petition was not its vehicle. (The candidate's 0.05 is recorded for the panel's rank-agreement, not graded here.)
