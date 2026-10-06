# Evaluation of claude-baseline — scotus/73374809, evt-petition-disposition

## Outcome and scores

Cert-stage cell (`event.yaml` stage `cert`). The petition was **denied** on
October 5, 2026, on first consideration after the September 28 long
conference: one distribution, no CVSG, no noted dissent (`outcome.json`,
`actual_granted` 0).

| field | value | how |
| --- | --- | --- |
| `correct` | 1 | `predicted_disposition` `denied` == `actual_disposition` `denied` |
| `brier_score` | 0.000025 | (0.005 − 0)² |
| `segment_base_rate` | 0.0512 | see below |
| `base_rate_basis` | `risk_set` | frozen `context.band` `baseline` + `context.salience_version` `sal-v4` |
| `brier_skill_score` | 0.9905 | 1 − 0.000025 / (0.0512 − 0)² |
| `reasoning_quality` | 0.88 | see below |

**Base rate.** The prediction's frozen context carries band `baseline` and
salience version `sal-v4`, matching the statpack table's heading, so the
basis is `risk_set`. Pooling the bracketed `reached` baseline figure,
resolved-weighted, over OT2017–OT2024 (the eight rendered Terms strictly
before Term 2025) gives 592.9 / 11,580 = 5.12%. The table renders 10 of 10
pack Terms, so there is no window divergence to flag. My own cell's
`record/context.json` band was not used.

## Reasoning quality (0.88)

The strongest rationale of the three, because it identifies the dispositive
legal fact and builds the number on it:

- **Independent state procedural ground.** It reads the judgment under review
  as a Court of Appeal dismissal for failure to procure the record, followed by
  a California Supreme Court denial without comment, and draws the right
  conclusion: no federal question was decided below, which would defeat review
  under 28 U.S.C. § 1257 regardless of drafting. The petition's own "Opinions
  Below" confirms the posture.
- **Correct anchor, shown.** It states the 5.1% pooled baseline reached rate
  with its table, names why that figure (not the terminal cut) is the
  yardstick, and reads the relist and CVSG cuts for shape only.
- **Well-ordered adjustments.** Non-justiciable questions as framed, improper
  respondent, no response and no waiver, no intervening decision for a GVR
  route. Each is a reason the petition sits in the weak tail of the baseline
  population, which is what justifies going an order of magnitude below the
  anchor.
- **Principled floor.** It explains why 0.005 rather than smaller: scoring-rule
  asymmetry at the extremes and a disclosed residual that the record might be
  attached to the wrong case, after its CourtListener lookup returned a stale
  caption for this docket id. That is honest calibration reasoning, and the
  data-quality disclosure is a point for the cell.

Where it falls short of the top: "Petitions with this profile are denied
essentially without exception" is asserted rather than tied to a cut, and the
corpus query it ran was uninformative by its own account, so the empirical
side rests entirely on the statpack. Minor.

The grade is of `reasoning.md` only; the forecast document and claims block
were read for context and are not scored here.

## Leakage

`mode` `forward`; `retrieved_outcome_material` false;
`influenced_prediction` `not_applicable`; `leakage_suspected` false. The
prediction was created September 17, 2026, eighteen days before the denial.
All 23 calls are `captured`. The one corpus query carries a
`retrieved_doc_date` of 2026-09-16 and returned recent application rows, not
this case; the one CourtListener lookup of docket id 73374809 carries a
`retrieved_doc_date` of 2026-05-21 and `date_terminated` null, so it
surfaced no disposition. Nothing post-dates the resolution, and nothing under
`data/qp-topics/` was read. The provisioned snapshot shows the case was
genuinely open, so the forward cell was not mis-provisioned.

## Big case

My independent read is 0.02: a pro se licensing dispute with no split, no
federal party, and a denial without comment. The candidate's 0.03 is in the
same place.
