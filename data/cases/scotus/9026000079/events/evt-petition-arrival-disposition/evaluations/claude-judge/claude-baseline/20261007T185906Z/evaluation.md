## Cell

Cert-stage arrival cell (`stage: cert`, `moment: arrival`), opened 2026-07-17 at docketing. Outcome: **denied** on 2026-10-05 after a single distribution (Conference of 9/28/2026), `actual_granted` 0, no noted dissent from denial. The provisioned snapshot shows a paid petition, paper-only filing directive (Rule 34.6), the Solicitor General's waiver of response on 2026-08-14, distribution on 2026-08-19, and the denial.

## Scores

- `correct` = 1: predicted `denied`, actual `denied` (exact label match on the cert axis).
- `brier_score` = (probability − 0)² = 0.000625.
- `segment_base_rate`, `brier_skill_score`: **omitted**; `base_rate_basis` null. The prediction's frozen context carries `band: baseline` under `salience_version: sal-v3`, but the committed `metrics/statpack.md` renders its "Segment base rate by salience band" table under **sal-v4** (its only such table). A band name only means something under the version that assigned it, so the rendered table is no baseline for this prediction, and the prompt's sole answer to a version mismatch is omission, never a `terminal` relabel. Recorded in this cell's `flags.json`. For the reader's orientation only (not a scored figure): the sal-v4 baseline band's bracketed `reached` figures pooled over OT2017–OT2025 come to roughly 5.4%, versus the ~6.6% the candidates computed from the sal-v3 table they saw; the difference is the version change, not an error by any candidate.
- `vote_accuracy`: omitted (cert stage; never scored).
- `judgment_correct`: null (no judgment on either side).
- `semantic_grades`: none written (cert cell; no semantic set declared; `semantic_claims` is null on the prediction).
- `claim_scores`: not mine; left absent for the harness.

## Leakage

Mode `forward`. `retrieved_outcome_material` false, `influenced_prediction` not_applicable, `leakage_suspected` false. The case was genuinely open at prediction time: the prediction was created 2026-08-16, the petition was not distributed until 2026-08-19 and not denied until 2026-10-05, and the 2026-08-16 snapshot the candidate read ended at the SG's waiver. Forward cell; prediction created 2026-08-16, before the 2026-08-19 distribution and the 2026-10-05 denial. Log (24 calls, capture coverage 1.0) shows CourtListener searches confined to the Ninth Circuit docket under review (retrieved_doc_date 2003-07-10, 2025-04-16, 2026-02-26 - all pre-petition), one corpus query of recent SCOTUS priors (retrieved_doc_date 2026-08-09, unrelated rows), and no query for this petition's own disposition. No data/qp-topics read. Reasoning states the docket showed the petition pending. No outcome material; the case was genuinely open.

## Reasoning quality: 0.85

What the rationale got right, and why it scores high:

- **Anchor.** It identified the scored yardstick correctly for an arrival cell — the baseline band's bracketed `reached` rate, pooled resolved-weighted over the rendered Terms strictly before OT2026 — and showed the arithmetic (862 / 13,163 ≈ 6.6% under the sal-v3 table it was shown). That is the right population and the right cut.
- **Adjustments tied to pre-decision facts the log corroborates.** Each downward step names a fact: an unpublished memorandum disposition submitted on the briefs without argument and without dissent; a threshold dismissal of a petition for review in a removal case; the SG's waiver; a solo immigration practitioner as counsel with no cert-stage amici; a neutral CA9 circuit cut. The captured CourtListener docket-entries call (retrieved_doc_date 2026-02-26) supports the lower-court trail it describes — memorandum disposition 2026-01-15, panel rehearing denied 2026-02-26, out-of-time amicus denied. The direction and rough magnitude of each adjustment are defensible, and the circuit cut is correctly read as carrying no information.
- **Calibrated restraint.** It states what keeps it off the floor (counseled paid petition; a possible § 1252 scope-of-review question with GVR potential) and names its main uncertainty plainly: the petition could not be read because of the paper-only directive and the memorandum text is unavailable in RECAP, so the forecast is a docket-skeleton read. That disclosure is exactly what a reader needs to weight the number.
- **Claim semantics stated.** It explains that `relist-increment` from a zero-distribution state is P(ever distributed) and keeps it apart from an expectation of relisting. (The claims block itself is scored in code and does not enter this grade.)
- **Hygiene.** It records that nothing retrieved disclosed a disposition and that it did not query for the outcome; the log bears that out.

What holds it below the top: the summary-disposition reasoning rests on a guessed question presented (that the dismissal turned on § 1252 review), which is inference stacked on inference, and the rationale leans on the 2026-08-14 waiver — legitimate signal in a forward cell, but it post-dates the arrival moment the event is defined at, and the rationale does not note that it is reading a later entry. Neither is an error; both are places where the reasoning is thinner than its confident tone. The outcome — denied at first conference, no writing — is the one the analysis predicted, for the reasons it gave.
