# Evaluation of codex-baseline — scotus/9026000173, evt-petition-disposition

## Outcome and scores

The event is a **cert** cell (`stage: cert`, moment `distribution`). The Court denied the petition on October 5, 2026 (`actual_disposition: denied`, `actual_granted: 0`), with no noted dissent, after one distribution of the petition itself (the August 26 distribution for the September 28 long conference; the May 19 distribution was of the linked fee motion, denied June 8).

- `correct` = 1: the candidate predicted `denied`, exact label match.
- `brier_score` = (0.015 − 0)² = 0.000225.
- `segment_base_rate` = 0.169, basis `risk_set`. The prediction's frozen context carries `band: elevated` **and** `salience_version: sal-v4`, and the committed `metrics/statpack.md` table "Segment base rate by salience band (sal-v4)" names the same version, so the bracketed `reached` figures apply. Pooled resolved-weighted over every rendered Term strictly before the case's Term 2026 (OT2017–OT2025, nine rows, weighted n = 3,085): 521.5 / 3,085 = 0.1690. The pack renders 10 of 10 Terms, so the rendered window is the pack's whole window and no lookback divergence arises; the unrounded `statpack.json` segments give 521 / 3,085 = 0.1689, the same number within rounding.
- `brier_skill_score` = 1 − 0.000225 / 0.169² = 0.9921.
- `vote_accuracy` omitted (cert stage; votes are never scored here).
- `claim_scores` and `process_version` left to the harness.

## Reasoning quality: 0.85

What drove the score. The rationale is the most carefully grounded of the three. It computes the prescribed anchor exactly as the contract asks (bracketed elevated reached rate pooled OT2017–OT2025, 16.888% from the unrounded pack fields), names it as the yardstick, and then departs from it on stated, case-specific grounds. Its five adjustments are each sound and each cites where in the record they come from: the first distribution belonged to the veteran fee motion rather than the petition, so the "two distributions" signal is weak; the asserted D.C./Ninth Circuit split overstates the disagreement, which the candidate checked by reading the two cited authorities (Lands Council v. Powell and James Madison Ltd. v. Ludwig) rather than taking the petition's characterization at face value; the vehicle is fact-dependent and reads as disputed application of a shared record-rule standard; the compound second question adds complications; and the Solicitor General's waiver with no response request supplies no attention signal. It correctly notes that a federal agency on the respondent side does not make this a federal-petitioner cell, states its conditional probabilities as conditionals, and is candid about limits (no lower-court opinion provisioned, the November 11 vs October 16 judgment-date discrepancy, no live corpus query).

Where it falls short. Having identified that the petition effectively sat at a first distribution with a waived federal respondent, pro se petitioner, and unpublished affirmance below, 1.5% is still generous against the posture its own analysis describes; the rationale does not quite close the loop between its vehicle findings and the number. It also reads the "elevated" band without asking what produced it, where the obvious answer (a distribution count inflated by the motion distribution) would have sharpened the case for a lower number. These are matters of calibration and emphasis, not errors of law or fact.

## Leakage

Forward cell. See `leakage.notes` in `evaluation.json`: the captured log shows no retrieval touching this petition's disposition. The three web-search rows are `unobserved`, so they are graded on their queries, which concern Supreme Court Rule 10 and the Court's rules page rather than this case. The CourtListener calls read two 1996 and 2005 circuit opinions the petition cites. `retrieved_outcome_material: false`, `influenced_prediction: not_applicable`, `leakage_suspected: false`. The case was genuinely open on September 18 (denial came October 5), so the forward provisioning was correct.

## Big case

My independent read, formed before weighing the candidate's: 0.05. One former employee's installation debarment, pro se, unpublished below, SG waived, denied without comment. The record-rule exceptions question has abstract importance but this petition was never going to be its vehicle. (The candidate's 0.25 reads the abstract question's stakes more generously than the vehicle warrants; that is recorded for the panel's rank-agreement, not graded here.)
