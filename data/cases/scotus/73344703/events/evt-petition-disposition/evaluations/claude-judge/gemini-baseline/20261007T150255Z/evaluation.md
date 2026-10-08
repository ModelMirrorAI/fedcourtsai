# Evaluation of gemini-baseline — scotus/73344703, evt-petition-disposition

## Outcome and scores

Cert-stage cell (`event.yaml` stage `cert`). Outcome: petition **denied** on 2026-10-05 after a single distribution to the 2026-09-28 long conference, no noted dissent, `actual_granted` 0.

| Field | Value | How |
| --- | --- | --- |
| `correct` | 1 | `predicted_disposition` `denied` == `actual_disposition` `denied` |
| `brier_score` | 0.0025 | (0.05 − 0)² |
| `segment_base_rate` | 0.0512 | frozen `context.band` `baseline` under `sal-v4`; statpack table heading is `sal-v4`; bracketed `reached` figures pooled resolved-weighted over OT2017–OT2024 (every rendered Term strictly before the case's Term 2025; n = 11,580) |
| `base_rate_basis` | `risk_set` | frozen band and salience version both present |
| `brier_skill_score` | 0.046 | 1 − 0.0025 / 0.0512² |

The caption renders 10 of 10 Terms, so the rendered window is the pack's window and no lookback divergence is flagged. `vote_accuracy` omitted (cert stage). No `semantic_grades` (no semantic set on a cert event). `claim_scores` left to the harness.

## Reasoning quality: 0.45

Right answer, thin analysis. The rationale correctly locates the `baseline` band's prior-Term rate ("~5-6%") and the 0-relist cut (1.2%), and correctly notes the petition rests on general First Amendment principles plus a summary-judgment complaint rather than a developed split, and that "disregarding record evidence" marks a fact-bound vehicle.

What holds the grade down:

- **The number is the anchor restated.** 0.05 is the band rate; the adjustment story ("slightly below the band's historical rate but above the 0-relist baseline, accounting for the possibility of it catching a clerk's eye due to the First Amendment context") mixes a risk-set rate with a terminal cut and then lands at the anchor anyway. The resulting skill score of 0.046 reflects that: the forecast parrots the baseline.
- **The case-specific weaknesses that made a grant near-impossible go unmentioned.** No state actor behind the First Amendment claim (private veterinarian's cease-and-desist letter), an unpublished state intermediate-court opinion, a CR 54(b) partial judgment raising a § 1257 finality question, and an unopposed distribution with no call for a response. All are on the face of the petition and the snapshot; the rationale reads the petition only through its QPs and a grep for "split".
- **Stated uncertainty is misplaced.** The "main uncertainty" offered is whether the state court's decision conflicts with other jurisdictions on anti-SLAPP, but the petition asserts a "state versus federal" split without conflicting holdings, and the court below did not decide the First Amendment question at all.
- **Disclosure inconsistency.** `retrieval.md` reads "No retrieval beyond the provisioned inputs" while the harness log shows a `fedcourts query` for "First Amendment anti-SLAPP social media" (results unobserved). Not leakage and not scored here, but a care point.

## Leakage: forward, not applicable

Mode `forward` per the log. The case was open at prediction (snapshot 2026-09-16; denial 2026-10-05). Every call's result is `unobserved` (coverage 0.0, this engine's standing shape), so the calls are graded on their queries: prompt and record reads, petition greps, `cat metrics/statpack.md`, and one corpus query bounded by `--decided-before 2026-09-16`. No call names this case's disposition, no `retrieved_doc_date` on or after 2026-10-05, no read under `data/qp-topics/`. The reasoning treats the petition as pending. `retrieved_outcome_material` false, `influenced_prediction` `not_applicable`, `leakage_suspected` false.

## Big case: 0.03

Formed from the record before reading the candidate's score. A private pet owner's intentional-tort suit against a veterinary clinic, from an unpublished Washington Court of Appeals opinion, fact-bound QPs, no amici, no response requested, denied silently. Negligible stakes beyond the parties.
