## Cell

Cert-stage arrival cell (`stage: cert`, `moment: arrival`), opened 2026-07-17 at docketing. Outcome: **denied** on 2026-10-05 after a single distribution (Conference of 9/28/2026), `actual_granted` 0, no noted dissent from denial. The provisioned snapshot shows a paid petition, paper-only filing directive (Rule 34.6), the Solicitor General's waiver of response on 2026-08-14, distribution on 2026-08-19, and the denial.

## Scores

- `correct` = 1: predicted `denied`, actual `denied` (exact label match on the cert axis).
- `brier_score` = (probability − 0)² = 0.0025.
- `segment_base_rate`, `brier_skill_score`: **omitted**; `base_rate_basis` null. The prediction's frozen context carries `band: baseline` under `salience_version: sal-v3`, but the committed `metrics/statpack.md` renders its "Segment base rate by salience band" table under **sal-v4** (its only such table). A band name only means something under the version that assigned it, so the rendered table is no baseline for this prediction, and the prompt's sole answer to a version mismatch is omission, never a `terminal` relabel. Recorded in this cell's `flags.json`. For the reader's orientation only (not a scored figure): the sal-v4 baseline band's bracketed `reached` figures pooled over OT2017–OT2025 come to roughly 5.4%, versus the ~6.6% the candidates computed from the sal-v3 table they saw; the difference is the version change, not an error by any candidate.
- `vote_accuracy`: omitted (cert stage; never scored).
- `judgment_correct`: null (no judgment on either side).
- `semantic_grades`: none written (cert cell; no semantic set declared; `semantic_claims` is null on the prediction).
- `claim_scores`: not mine; left absent for the harness.

## Leakage

Mode `forward`. `retrieved_outcome_material` false, `influenced_prediction` not_applicable, `leakage_suspected` false. The case was genuinely open at prediction time: the prediction was created 2026-08-16, the petition was not distributed until 2026-08-19 and not denied until 2026-10-05, and the 2026-08-16 snapshot the candidate read ended at the SG's waiver. Forward cell; prediction created 2026-08-16, before distribution (2026-08-19) and denial (2026-10-05). Log (7 calls, coverage 1.0): scripted shell batches reading the prompt, schemas, record and statpack; one 'other' call whose payload is a harness credential redaction ([redacted:fernet-token]), not outcome material; no retrieved_doc_date on any row. The CourtListener search the candidate reports (bounded to filings before 2026-02-01, returned 429) does not appear as a distinct mcp row - a capture observation, not a leakage signal. No query for this petition's outcome; no data/qp-topics read.

## Reasoning quality: 0.70

A methodologically careful rationale with no errors in it, whose weakness is that it chose to use less information than the provisioned record offered.

What it got right:

- **Anchor, stated precisely.** It pooled the bracketed `reached` rate over the rendered Terms strictly before OT2026 (863 / 13,163 = 6.56%), explained why that is the arrival anchor rather than the terminal relist-zero rate, and correctly treated the CA9 cut as a secondary comparison that blends fee classes. This is the cleanest statement of the base-rate discipline among the three candidates.
- **Claim semantics.** It explains that `relist-increment` from zero distributions means an initial distribution, not a repeated conference, and that a CVSG is practically unavailable where the Solicitor General already represents the respondent. (The claims block is scored in code and does not enter this grade.)
- **Honesty about retrieval.** One CourtListener search, bounded to pre-petition filings, returned 429; the rationale says so and says nothing informed the number beyond the snapshot and statpack.
- **A defensible reading of the moment.** It declined to use the 2026-08-14 waiver as an arrival-time signal because the event is defined at docketing. In a forward cell that entry is legitimate signal, so the restraint cost it information, but it is a principled choice and it is stated.

What holds the grade down:

- **Under-use of the snapshot.** The provisioned record alone carried usable signal that the rationale set aside: the respondent is the Attorney General represented by the SG, which marks an immigration removal case (a very high-volume, very high-denial class); the lower court is the Ninth Circuit with rehearing denied; the filing is paper-only; counsel of record is a solo practitioner. The rationale explicitly declined even to read the caption as a signal ("did not infer the underlying legal issue from the party names"). That is over-cautious: the class of case is a legitimate pre-decision fact, not an inference about the question presented.
- **A single retrieval attempt.** After one 429 it made no second attempt, no corpus query, and no other route to the lower-court disposition, so the forecast stayed at a near-anchor 5% by default rather than by analysis. The number was the least sharp of the three, and the rationale explains that as a choice ("found no case-specific basis for a substantial upward adjustment") when the question was whether there was basis for a *downward* one — and there was, in the snapshot.

Net: sound where it reasons, but it reasons about less than it could have. The outcome was the one it predicted.
