# Evaluation of gemini-baseline — scotus/73374809, evt-petition-disposition

## Outcome and scores

Cert-stage cell (`event.yaml` stage `cert`). The petition was **denied** on
October 5, 2026, on first consideration after the September 28 long
conference: one distribution, no CVSG, no noted dissent (`outcome.json`,
`actual_granted` 0).

| field | value | how |
| --- | --- | --- |
| `correct` | 1 | `predicted_disposition` `denied` == `actual_disposition` `denied` |
| `brier_score` | 0.000001 | (0.001 − 0)² |
| `segment_base_rate` | 0.0512 | see below |
| `base_rate_basis` | `risk_set` | frozen `context.band` `baseline` + `context.salience_version` `sal-v4` |
| `brier_skill_score` | 0.9996 | 1 − 0.000001 / (0.0512 − 0)² |
| `reasoning_quality` | 0.45 | see below |

**Base rate.** The prediction's frozen context carries band `baseline` and
salience version `sal-v4`, matching the statpack table's heading, so the
basis is `risk_set`. Pooling the bracketed `reached` baseline figure,
resolved-weighted, over OT2017–OT2024 (the eight rendered Terms strictly
before Term 2025) gives 592.9 / 11,580 = 5.12%. The table renders 10 of 10
pack Terms, so there is no window divergence to flag. My own cell's
`record/context.json` band was not used.

## Reasoning quality (0.45)

The call was right and the direction of every adjustment was right, but the
rationale is a single paragraph that asserts more than it analyzes:

- **Wrong anchor.** It cites "the baseline grant rate for such petitions is
  1.2%." That is the `granted` share of the relist-0 bucket in the paid-segment
  relist cut, a terminal, all-Term figure, not the frozen band's risk-set
  reached rate pooled over strictly-prior Terms that the contract and the
  table's own caption name as the yardstick (5.1%). The two differ by a factor
  of four and are from different populations. The final number happens to sit
  below both, so the error did not move the headline, but the stated anchor is
  the wrong one.
- **"Frivolous" is asserted, not shown.** The rationale never engages the
  posture that actually decides this petition: the Court of Appeal refused the
  appeal for a record deficiency and the California Supreme Court denied review
  without comment, so no federal question was passed on below. The petition's
  "Opinions Below" states as much. The grounds given (pro se, no split, no
  coherent question) are correct but generic.
- **No information-set discipline.** Nothing says what was read, what was
  missing (no BIO, no lower-court orders), or how much weight the petition's
  own factual claims were given.
- **Credit where due.** It correctly identified the pro se posture, the state
  appellate court as respondent, the baseline band, the single distribution,
  and the absence of any genuine federal interest for a CVSG, and it reasoned
  the relist and dissent probabilities in the right direction.

The grade is of `reasoning.md` only; the forecast document and claims block
were read for context and are not scored here.

## Leakage

`mode` `forward`; `retrieved_outcome_material` false;
`influenced_prediction` `not_applicable`; `leakage_suspected` false. The
prediction was created September 17, 2026, eighteen days before the denial.
All 18 logged calls are `unobserved` (capture coverage 0.0, an engine's
standing shape rather than a defect), so each is graded on its query: file
reads of the provisioned record, prompt, and statpack, then the write-out. No
web, MCP, or corpus call; nothing names this case outside the provisioned
paths; nothing under `data/qp-topics/` was read. `retrieval.md` says no
retrieval beyond the provisioned inputs, which the query shapes bear out. The
provisioned snapshot shows the case was genuinely open, so the forward cell
was not mis-provisioned.

## Big case

My independent read is 0.02: a pro se licensing dispute with no split, no
federal party, and a denial without comment. The candidate's 0.01 is in the
same place.
