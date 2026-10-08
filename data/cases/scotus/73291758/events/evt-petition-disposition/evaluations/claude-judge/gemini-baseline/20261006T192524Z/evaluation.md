# Evaluation: gemini-baseline — scotus/73291758, evt-petition-disposition

Cert-stage cell (event stage `cert`, moment `distribution`). Outcome: petition
**denied** 2026-10-05 after a single distribution for the 2026-09-28 long
conference, `actual_granted` 0, no noted dissent, no response ever requested.

## Quantitative

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.001 − 0)² = 0.000001.
- `segment_base_rate` = 0.0512 (`base_rate_basis` `risk_set`). The prediction
  froze `band: baseline` under `salience_version: sal-v4`, and the committed
  statpack's segment table is headed "(sal-v4)", so the versions match. Pooled
  the bracketed `reached` figure, weighted by its `n`, over Term rows strictly
  before the case's Term 2025 — OT2017 through OT2024, all eight the table
  renders (caption: 10 of 10 Terms rendered, so the rendered window is the
  pack's window and no divergence arises): 593 / 11,580 = 0.05120. The
  unrounded JSON rates pool to 0.05121, the same to four decimals.
- `brier_skill_score` = 1 − 0.000001 / 0.0512² = 0.9996.
- `vote_accuracy` omitted (cert cell; no votes forecast anyway).

## Reasoning quality: 0.45

The call was right and the anchor was right: the rationale names the ~5.1%
prior-Term baseline-band rate, correctly identifies the petition as pro se,
fact-bound, and splitless, and adjusts downward. That much is sound.

Three things pull the grade down, and they are about the analysis rather than
the number:

1. **An asserted docket fact that is not in the record.** The rationale says
   "the respondents waived their right to respond." The docket carries no
   waiver entry: the petition was filed with a response due June 3, 2026, the
   deadline lapsed, and the case was distributed June 17 — three entries in
   total, none a waiver. (This check is valid for a forward cell: the decided
   docket's entries are a superset of the prediction's snapshot, so an entry
   absent now was absent then.) A non-response and a waiver are different
   signals, and the prompt contract's "never invent facts" rule is pointed at
   exactly this.
2. **A terminal cut read as a conditional rate.** "This case has zero relists
   (base rate ~1.2%)" takes the paid-segment relist-count-0 *terminal* row as
   the rate a once-distributed petition faces, which is the terminal/risk-set
   conflation the statpack's own caption warns against. The other two
   candidates either used it only as a corroborating cut or explicitly refused
   the substitution.
3. **The strongest vehicle defect is missed.** The petition itself concedes the
   constitutional claims were not raised at the hearing and were rejected on
   that basis on appeal. Forfeiture below, and the adequate-and-independent
   state-ground problem it creates, is the single best reason this petition
   could not be granted, and the rationale never mentions it; it gestures at
   "ineffective assistance in a civil context" without drawing the point.

The one-paragraph rationale also does not engage with where the residual mass
sits (a stray GVR, a reschedule), so 0.001 is asserted rather than argued.

## Leakage

Forward cell; `influenced_prediction` `not_applicable`, `retrieved_outcome_material`
false, `leakage_suspected` false. The log's `result_capture_coverage` is 0.0,
an engine's standing shape, so every call is graded on its query: all 25 are
local reads of the prompt, provisioned inputs, and statpack greps, with no
external call of any kind. The prediction (2026-09-16) predates the denial
(2026-10-05) and the provisioned snapshot showed the case open; no
mis-provisioning. The candidate's `retrieval.md` reports no retrieval, which
the log bears out.

## Big case

My independent read is 0.03 (see `big_case.notes`): a private family
protective-order dispute with no institutional party, no split, and forfeited
federal claims; the outcome (silent denial, no relist) is consistent with that.
