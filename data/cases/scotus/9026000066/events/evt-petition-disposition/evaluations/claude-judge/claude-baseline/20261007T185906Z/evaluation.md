# Evaluation — claude-baseline, scotus/9026000066, evt-petition-disposition

## Outcome and scores

Cert-stage cell (`event.yaml` stage `cert`, moment `distribution`). The
petition in *Smith v. Smith*, No. 26-66, was denied on 2026-10-05 after one
distribution for the 2026-09-28 long conference, with no noted dissent
(`outcome.json`: `actual_disposition: denied`, `actual_granted: 0`).

| Field | Value |
| --- | --- |
| `predicted_disposition` / `correct` | `denied` / 1 |
| `probability` / `brier_score` | 0.005 / 0.000025 |
| `segment_base_rate` (`risk_set`) | 0.0502 (n = 12,720) |
| `brier_skill_score` | 0.9901 |
| `reasoning_quality` | 0.88 |

**Base rate.** The prediction froze `band: baseline` under `salience_version:
sal-v4`, matching the statpack table's heading, so the basis is `risk_set`:
the bracketed `reached` figure pooled resolved-weighted over the rendered
Terms strictly before 2026 (2017–2025; the caption renders 10 of 10 Terms, so
no window divergence). From `metrics/statpack.json`: 638.0 / 12,720 = 0.05016.
The candidate's own pooling (5.0%, n = 12,720) is the same number.

## What the prediction got right and wrong

Right on every scored axis: a clean first-conference denial, no further
distribution, no writing — exactly the forecast. The 0.5% forecast scored
marginally worse than a 0.1% one would have, but the document explains why it
did not go lower, and that reasoning is sound under a proper scoring rule.

## Reasoning quality (0.88)

This is a well-built rationale. Its strengths:

- **The anchor is computed, stated, and correctly framed.** It pools the
  baseline band's `reached` rate over 2017–2025 by `n`, contrasts it with the
  terminal (`ended`) figure, and says which one is scored and why. The number
  matches mine exactly.
- **The adjustments are specific and sourced.** Pro se paid status (from the
  snapshot's attorney field and the petition's signature); the decision below
  is an unpublished Arizona memorandum decision with review denied by the
  state supreme court; the statpack's originating-court cuts (the `ariz`
  row is 30 of 30 denied — I checked, it is); the questions presented read in
  full, with the *Lee v. Kemna* inadequate-state-ground framing of Question 1
  correctly identified as the only hook and correctly dismissed as a vehicle
  argument rather than a reason to grant; no brief in opposition, no waiver, no
  call for a response, distributed anyway; no intervening decision for a GVR.
  Every one of these is a fact in the provisioned record or the committed
  statpack, and every one points the right way.
- **Calibration is argued, not asserted.** The document says why it stopped
  at 0.5% rather than lower (proper scoring, residual mass on unseen
  paths) and names the conditions under which it would be wrong.
- **Candour about what it could not see.** Four CourtListener searches
  returned nothing, so its view of the decision below is the petitioner's
  account; it says so, and it notes the snapshot postdates the conference but
  carries no order.

What keeps it from higher: the relist reasoning reads the band's 24%
"left the band" share as the rate of acquiring another distribution, which
conflates band strengthening with relisting (a petition can leave `baseline`
by a response request or amicus, not only by relist); and the
`summary-disposition-route` conditional of 0.6 is shaded above the
statpack's own cert-order share on a thin argument. Both belong to the claims
block, which is scored in code, so they weigh only lightly here as a matter of
analytical care. The core cert analysis is as good as this record allows.

## Leakage

Mode `forward`; the prediction (2026-10-04) predates the resolution
(2026-10-05). Capture coverage 1.0, so results are real evidence. The one
corpus query (`fedcourts query --court scotus --era 2020s --disposition
denied`) returned recency-ranked rows whose newest `retrieved_doc_date` is
2026-10-02, before this event resolved, and the query did not target this
case. The four CourtListener `search` calls targeted the Arizona decision
and this docket by number and name and, per the candidate's note, returned
zero results; nothing in the log carries a date on or after 2026-10-05.
`retrieved_outcome_material: false`, `influenced_prediction:
not_applicable`, `leakage_suspected: false`.

## Big case

My independent read is 0.02: a two-party divorce appeal from an unpublished
state memorandum decision, denied without a writing. Formed from the record
and the outcome before consulting the candidate's own score.

## Not applicable on this cell

No `vote_accuracy` (cert stage), no `judgment_correct`, no `semantic_grades`
(no semantic set on a cert event; `record/opinion/` absent as expected), no
`claim_scores` (harness-computed). The forecast document was read for
context only and is not scored.
