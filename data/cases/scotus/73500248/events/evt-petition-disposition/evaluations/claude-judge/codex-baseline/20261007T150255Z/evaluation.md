# Evaluation of codex-baseline — Webb v. Trombley, No. 25-1346 (evt-petition-disposition)

## Outcome and scores

Cert-stage cell (`event.yaml` stage `cert`, moment `distribution`). The petition was
**denied** on the October 5, 2026 order list after a single distribution for the
September 28 conference, with no call for a response and no noted dissent.

- `predicted_disposition` denied vs `actual_disposition` denied → `correct` = 1.
- `probability` 0.025, `actual_granted` 0 → `brier_score` = 0.000625.
- `segment_base_rate` = 0.0512, basis `risk_set`. The prediction froze band `baseline`
  under `sal-v4`; the statpack's "Segment base rate by salience band (sal-v4)" heading
  matches. Bracketed `reached` figure pooled resolved-weighted over the rendered Terms
  strictly before Term 2025 (OT2017–OT2024, weighted n = 11,580) = 5.12%. The table
  renders 10 of 10 Terms, so no window-divergence flag.
- `brier_skill_score` = 1 − 0.000625 / 0.0512² = 0.7616.
- `vote_accuracy` omitted (cert stage). `judgment_correct` null. No `semantic_grades`
  block (cert cell).

## Reasoning quality: 0.85

A careful, well-sourced rationale that gets the structure of the problem right and is
candid about what it is and is not doing.

Strengths. The information boundary is stated precisely (forward cell, the 2026-09-17
snapshot, the July 18 petition fetch, no BIO because of the waiver, no outcome sought or
encountered). The calibration anchor is computed rather than eyeballed: the same
OT2017–OT2024 pooled reached rate I reach, 5.12% on n = 11,580, with the correct
exclusion of the case's own Term and an explicit refusal to substitute the terminal rate.
The candidate also correctly refuses to treat the all-Term relist and CVSG cuts as
transition probabilities from this petition's one-distribution state. The legal analysis
engages the petition itself: the $15,000 verdict against a $206,977.50 fee request shows
why the cap was outcome-determinative; the Second Circuit's footnote 3 is read for what
it says (every circuit to reach the cap question agrees); the petition's asserted splits
on appellate fees, pre-incarceration conduct, and injunctive relief are correctly
diagnosed as collateral to the question presented; and *Murphy v. Smith* was actually read
and correctly characterised as not deciding the 150% question while treating the cap as
background. The downward move from 5.1% to 2.5% is attributed to selection-type reasons
(no direct conflict, no attention signal, a nonprecedential order below) rather than to a
view of the merits, which is the right frame for a cert forecast, and the upward
considerations that keep it off the floor are named.

Weaknesses, modest. A fair amount of the "Calibration" section recites statpack
population figures the candidate then says it is not using, which pads the document
without changing the number. The claim that the waiver provides "no affirmative signal"
is right but under-uses it: the strongest docket fact here is that no call for a
response had issued eleven days before conference, and this rationale leaves that
inference implicit where it could have carried more of the downward move. The statement
that the Term is 2025 "not 2026" is correct for the docket-number Term but is asserted
rather than explained. The 2.5% itself is well inside the range the analysis supports;
it is slightly less sharp than the evidence warranted given a waiver, no CFR, and a
uniform consensus, which is a calibration remark rather than a reasoning fault.

The forecast document was read for context only and is not scored here.

## Leakage: forward, not applicable

`retrieval_log.json` records `mode: forward`, coverage 0.93. Captured calls read the
prompt, the provisioned snapshot, context and petition text, and the committed statpack
and statpack JSON; two uncaptured web searches targeted *Murphy v. Smith* and Rule 10
(graded on their queries: neither names this petition); CourtListener calls fetched and
searched *Murphy v. Smith*, filed 2018-02-21. No call queried this case's caption or
docket, and no `retrieved_doc_date` is at or after 2026-10-05. The prediction was created
2026-09-17; the order issued 2026-10-05, so the case was open when the cell ran. The
candidate's own disclosure that it did not seek or encounter the outcome is consistent
with the log. `retrieved_outcome_material` false, `influenced_prediction`
not_applicable, `leakage_suspected` false.

## Big case (independent read): 0.15

Same read as across the cell: a single PLRA fee-cap statutory question with uniform
circuit agreement, a $15,000 verdict, a private prisoner-plaintiff against state officers,
a summary order below, and a silent denial. Meaningful to the prisoner civil-rights bar,
low general salience. Formed before weighing the candidate's own score; no agreement
number computed.
