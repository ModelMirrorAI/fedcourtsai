# Evaluation of claude-baseline — scotus/73344703, evt-petition-disposition

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

## Reasoning quality: 0.88

The strongest of the three rationales: a complete record read, the right anchor, and the decisive procedural point.

- **Anchor done right, with cross-checks.** Pools the `sal-v4` `baseline` bracketed `reached` rates over OT2017–OT2024 to 5.1% on n = 11,580 (matching this evaluation), then reads the terminal `baseline` row, the 0-relist cut, and the no-CVSG cut from the same pack as context, correctly labelled as terminal cuts rather than substitute anchors.
- **Every real vehicle defect, stated sharply.** No state actor behind the First Amendment claim, and the court below did not decide that question, so QP1 was not passed upon; QP2 asks a state court to be held to federal Rule 56 doctrine (*Tolan*) that does not bind it; the asserted "state versus federal" split has no conflicting holdings; an unpublished intermediate-court opinion; a CR 54(b) partial judgment with negligence claims still live, raising § 1257 finality. All verifiable in the provisioned petition.
- **The decisive inference.** The petition was distributed with no brief in opposition and no waiver entry, and the Court does not grant without first calling for a response, so any grant path required a call and a redistribution the record gave no reason to expect. That is the fact that made denial at the 9/28 conference near-certain, and only this candidate draws it.
- **Good forward hygiene.** Confirmed via CourtListener that the docket was open (`date_terminated` null, last modified 2026-07-01) to rule out a mis-provisioned decided case, and disclosed that the corpus queries did not inform the number.
- **Tells the reader where to discount it**: finality inferred from the petition's own description, waiver status unconfirmable, and the 5.1% class floor named as the figure it moved away from.

Minor deductions: the Rule 15.5 citation for the unopposed-distribution point is slightly off (Rule 15.5 governs when the Clerk distributes, the no-grant-without-response practice is convention), and the claim that a grant without a response is "essentially unheard of" is stated as fact where "exceedingly rare" is the defensible form. Neither affects the analysis.

## Leakage: forward, not applicable

Mode `forward` per the log; the case was open at prediction (snapshot 2026-09-16; denial 2026-10-05). Capture coverage 1.0. The CourtListener `get_endpoint_item` on this docket carries `retrieved_doc_date` 2026-05-14 (the filing date) and returned `date_terminated` null; `docket-entries` returned 0 rows. Two `fedcourts query --era 2020s` corpus calls (doc date 2025-02-11) returned unrelated granted and application rows. No `retrieved_doc_date` on or after 2026-10-05, no disposing order, no read under `data/qp-topics/`. `retrieval.md` discloses all of it. `retrieved_outcome_material` false, `influenced_prediction` `not_applicable`, `leakage_suspected` false.

## Big case: 0.03

Formed from the record before reading the candidate's score. A private pet owner's intentional-tort suit against a veterinary clinic, from an unpublished Washington Court of Appeals opinion, fact-bound QPs, no amici, no response requested, denied silently. Negligible stakes beyond the parties.
