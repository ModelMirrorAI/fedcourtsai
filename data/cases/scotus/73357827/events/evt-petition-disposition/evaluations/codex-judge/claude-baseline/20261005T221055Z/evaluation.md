# Evaluation: claude-baseline

## Outcome and numerical score

This is a cert-stage evaluation of Wisconsin Voter Alliance v. Millis,
No. 25-1288. The supplied outcome records denial on October 5, 2026,
with `actual_granted = 0`. The October 5 provisioned snapshot also records
"Petition DENIED." The candidate's September 16 prediction names `denied`,
so `correct = 1`. Its grant probability of 0.015 yields
`brier_score = (0.015 - 0)^2 = 0.000225`.

The baseline comes from the prediction's own frozen `baseline` band,
`sal-v4` version, and docket Term 2025, not the evaluator's terminal context.
The committed statpack's sal-v4 heading matches. I use the bracketed reached
rates for every rendered strictly prior Term, 2017–2024, resolved-weighted:

| Term | Reached rate | Weighted resolved n |
| --- | --- | --- |
| 2017 | 4.7% | 1643 |
| 2018 | 4.6% | 1524 |
| 2019 | 4.6% | 1399 |
| 2020 | 4.5% | 1739 |
| 2021 | 5.6% | 1500 |
| 2022 | 5.8% | 1192 |
| 2023 | 5.9% | 1312 |
| 2024 | 5.7% | 1271 |

The weighted sum of the displayed rates is 592.925 over 11,580, giving
`segment_base_rate = 0.05120250431778929`, on the `risk_set` basis.
The numerator is a reconstruction from rounded published rates, not an
integer count of grants. The resulting single-event skill is
`1 - 0.000225 / 0.05120250431778929^2 = 0.9141777072871346`.
The table renders 10 of 10 available Terms; 2025 and 2026 are excluded.
No rendered-window truncation requires a flag. This uses the committed pack
as supplied, not a newly queried corpus or a claim about remote freshness.

## Reasoning quality: 0.85

The rationale meaningfully distinguishes a petition's asserted HAVA-wide
conflict from the narrower administrative-complaint provision and from the
standing ground supporting the judgment. The provisioned petition's own
account, printed pp. 13–18, supports examining those distinctions rather
than treating its circuit tally as dispositive. The candidate also grounds
its discount in the response waiver, first distribution, and lack of a
response request in its stated information set, and balances those negatives
against the concurrence, amicus support, and federal enforcement interest.
Its acknowledgment of the missing district-court record and lack of useful
corpus comparators makes the evidentiary limits clear.

The remaining deductions are methodological, not punishment for uncertainty:
the statement that the section 1983 route is largely closed after Medina is
broader than the provision-specific analysis supplied in the rationale;
terminal no-relist and no-CVSG rates are not direct probabilities for a live
first-conference petition; and counsel's prior unsuccessful filings provide
only weak support for this petition's prospects. The reduction from about
5.1% to 1.5% is reasoned but judgmental rather than empirically estimated.
The denial is consistent with the forecast, but the supplied outcome gives
no substantive explanation and does not establish that the Court adopted
any of these proposed reasons.

This score evaluates only `reasoning.md`. The forecast document was read for
context, not graded. No quantitative claim scores or semantic grades are
supplied. Vote accuracy is omitted because cert votes are not scored.
The optional independent stakes assessment is omitted.

## Leakage assessment

The harness log labels the prediction `forward`; the run and its recorded
retrieval occurred September 16, before the October 5 resolution. All 49
calls carry captured results, although the staged log contains query slices
and result metadata rather than complete returned bodies. The searches and
reads concern lower-court decisions, the petition's pre-decision filings,
and contextual statistics. The logged July 7 document date and the other
cases' cert denials described in the rationale predate this event's
resolution; neither is this petition's outcome. No query or rationale shows
an already-decided target petition. A correctly forecast order-list date
does not independently establish leakage.

Accordingly, `retrieved_outcome_material = false`,
`influenced_prediction = not_applicable`, and `leakage_suspected = false`.
The decided October 5 snapshot I read is evaluator evidence, not a claim
about what was in the candidate's September 16 snapshot.
