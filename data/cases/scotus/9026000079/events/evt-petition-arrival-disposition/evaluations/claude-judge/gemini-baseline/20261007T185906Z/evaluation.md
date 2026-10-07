## Cell

Cert-stage arrival cell (`stage: cert`, `moment: arrival`), opened 2026-07-17 at docketing. Outcome: **denied** on 2026-10-05 after a single distribution (Conference of 9/28/2026), `actual_granted` 0, no noted dissent from denial. The provisioned snapshot shows a paid petition, paper-only filing directive (Rule 34.6), the Solicitor General's waiver of response on 2026-08-14, distribution on 2026-08-19, and the denial.

## Scores

- `correct` = 1: predicted `denied`, actual `denied` (exact label match on the cert axis).
- `brier_score` = (probability − 0)² = 2.5e-05.
- `segment_base_rate`, `brier_skill_score`: **omitted**; `base_rate_basis` null. The prediction's frozen context carries `band: baseline` under `salience_version: sal-v3`, but the committed `metrics/statpack.md` renders its "Segment base rate by salience band" table under **sal-v4** (its only such table). A band name only means something under the version that assigned it, so the rendered table is no baseline for this prediction, and the prompt's sole answer to a version mismatch is omission, never a `terminal` relabel. Recorded in this cell's `flags.json`. For the reader's orientation only (not a scored figure): the sal-v4 baseline band's bracketed `reached` figures pooled over OT2017–OT2025 come to roughly 5.4%, versus the ~6.6% the candidates computed from the sal-v3 table they saw; the difference is the version change, not an error by any candidate.
- `vote_accuracy`: omitted (cert stage; never scored).
- `judgment_correct`: null (no judgment on either side).
- `semantic_grades`: none written (cert cell; no semantic set declared; `semantic_claims` is null on the prediction).
- `claim_scores`: not mine; left absent for the harness.

## Leakage

Mode `forward`. `retrieved_outcome_material` false, `influenced_prediction` not_applicable, `leakage_suspected` false. The case was genuinely open at prediction time: the prediction was created 2026-08-16, the petition was not distributed until 2026-08-19 and not denied until 2026-10-05, and the 2026-08-16 snapshot the candidate read ended at the SG's waiver. Forward cell; prediction created 2026-08-16, before distribution (2026-08-19) and denial (2026-10-05). Log (21 calls) has capture coverage 0.0 - every row unobserved, an engine's standing shape - so each call is graded on its query: one CourtListener dockets call for this docket id (reported as HTTP 429), one web search for the Ninth Circuit decision ("Acosta-Tapia" "Ninth Circuit" 25-2460), one corpus query bounded --decided-before 2026-08-16. None targets this petition's outcome, which did not exist yet. No data/qp-topics read. The candidate disclosed the web fallback in reasoning.md and retrieval.md.

## Reasoning quality: 0.50

The rationale is short, directionally sound, and honest about its tooling, but its analysis has real weaknesses that the correct outcome does not cure.

What it got right:

- **Anchor.** It states the prior-Term pooled rate for the paid baseline band as "around 6.5%" — the right figure under the table it was shown — and adjusts from there rather than from a terminal rate.
- **Vehicle read.** An unpublished, fact-bound immigration memorandum with the SG waiving is a weak vehicle, and denial was the right call.
- **Disclosure.** It says plainly that the CourtListener call returned HTTP 429, that it fell back to a web search, and that no documents were provisioned. That candour is a point for the cell.

What pulls the grade down:

- **The factual core is unverifiable from the record.** The two specific facts the rationale rests on — dismissal as untimely under 8 U.S.C. § 1252(b)(1), and an underlying negative reasonable-fear determination — come from a single web search whose result the log did not capture (every row in this candidate's log is `unobserved`). Nothing else in the record confirms them; the only corroborated fact is that the Ninth Circuit dismissed the petition for review. The rationale presents the search result as settled ("Web retrieval confirms") without flagging that it rests on one uncaptured hit.
- **The untimeliness inference is analytically weak.** The rationale treats an untimeliness dismissal as a "fatal procedural barrier" to certiorari. But whether the § 1252(b)(1) deadline is jurisdictional or a claim-processing rule, and how it applies, is the kind of question the Court has recently taken up; a timeliness dismissal can be the question presented rather than a bar to review. The candidate's own forecast document half-concedes this ("unless there is an intervening decision directly on the timeliness standard"), and the rationale never reconciles the two.
- **The SG waiver is over-read.** The rationale says the waiver signals that "the respondent sees no circuit split or important federal question." The SG waives routinely on low-salience petitions, and the Court can call for a response; a waiver is a modest denial-side signal, not evidence about the merits of the split claim.
- **0.005 is thinly justified.** The number sits below the baseline band's own terminal (relist-zero) rate of roughly 1%, with no argument for why this petition is less likely to be granted than the average petition that ends in the weakest band. The Brier reward for an extreme number on a denial is not evidence of sound reasoning; the grade is for the argument.

Outside the grade (claims are scored in code, not here): the rationale offers no account of its claim numbers, and the forecast document's "zero relists" framing sits uneasily beside a `relist-increment` of 0.01 from a zero-distribution state. I note it because the rationale's silence on claim semantics is part of why the document reads as thin; the claim values themselves do not enter `reasoning_quality`.
