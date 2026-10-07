# Evaluation of codex-baseline — scotus/73344703, evt-petition-disposition

## Outcome and scores

Cert-stage cell (`event.yaml` stage `cert`). Outcome: petition **denied** on 2026-10-05 after a single distribution to the 2026-09-28 long conference, no noted dissent, `actual_granted` 0.

| Field | Value | How |
| --- | --- | --- |
| `correct` | 1 | `predicted_disposition` `denied` == `actual_disposition` `denied` |
| `brier_score` | 0.0001 | (0.01 − 0)² |
| `segment_base_rate` | 0.0512 | frozen `context.band` `baseline` under `sal-v4`; statpack table heading is `sal-v4`; bracketed `reached` figures pooled resolved-weighted over OT2017–OT2024 (every rendered Term strictly before the case's Term 2025; n = 11,580) |
| `base_rate_basis` | `risk_set` | frozen band and salience version both present |
| `brier_skill_score` | 0.962 | 1 − 0.0001 / 0.0512² |

The caption renders 10 of 10 Terms, so the rendered window is the pack's window and no lookback divergence is flagged. `vote_accuracy` omitted (cert stage). No `semantic_grades` (no semantic set on a cert event). `claim_scores` left to the harness.

## Reasoning quality: 0.85

A careful, well-grounded rationale whose downward adjustment from the anchor is earned rather than asserted.

- **Anchor done right.** Pools the `sal-v4` `baseline` bracketed `reached` rates over OT2017–OT2024 to 5.12% on n = 11,580, the same figure this evaluation computes, and states that the rounded percentages make it approximate and that it is the private-petitioner risk set, not a terminal or segment-wide rate.
- **The vehicle defects are the real ones.** Identifies that QP2 is fact-specific error correction and that the petition concedes the court below stated the governing standards correctly; that QP1 runs against a private business with no attributable state action, citing *Manhattan Community Access Corp. v. Halleck* as the obstacle; that the opinion below is unpublished; and that the CR 54(b) certification raises finality and adequate-state-ground uncertainty. Each is verifiable in the provisioned petition (the unpublished opinion at its "Opinions Below", CR 54(b) at p. 16, the cease-and-desist letter throughout).
- **Checked an authority instead of trusting the petition's gloss.** Pulled *Tolan v. Cotton* from CourtListener and correctly distinguished it as a federal § 1983 summary vacatur, with Justice Alito's concurrence on Rule 10's error-correction reluctance treated as context, not holding.
- **Disciplined about its information set.** Says what the snapshot does and does not show (no response, no request, no amicus), that absence of a BIO on disk is not independent confirmation, and that web attempts returned nothing usable.

Marked down from the top band for two things. It does not draw the single most decisive procedural inference, that a petition distributed without a response is essentially never granted without a call for a response first, which is what made a grant at the 9/28 conference practically foreclosed. And it mildly over-hedges the state-law dilution point without reaching the sharper fact that the court below never decided the First Amendment question, so QP1 was not passed upon.

## Leakage: forward, not applicable

Mode `forward` per the log; the case was open at prediction (snapshot 2026-09-16; denial 2026-10-05). Capture coverage 0.86. The four web rows are `unobserved` and are graded on their queries: Rule 10 and supremecourt.gov rules pages, nothing about this case. CourtListener calls fetched *Tolan* and *Halleck*, general precedent. The shell find explicitly excludes `data/qp-topics/`. No call names this docket, no `retrieved_doc_date` on or after 2026-10-05, no disposing order. `retrieval.md` discloses the same set. `retrieved_outcome_material` false, `influenced_prediction` `not_applicable`, `leakage_suspected` false.

## Big case: 0.03

Formed from the record before reading the candidate's score. A private pet owner's intentional-tort suit against a veterinary clinic, from an unpublished Washington Court of Appeals opinion, fact-bound QPs, no amici, no response requested, denied silently. Negligible stakes beyond the parties.
