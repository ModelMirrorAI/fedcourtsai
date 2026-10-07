# Evaluation: gemini-baseline

## Outcome and quantitative scores

The supplied cert-stage outcome is denial on October 5, 2026, with
`actual_granted = 0`. gemini-baseline predicted `denied` on September 17 with
grant probability 0.05. The exact-label score is **1** and the Brier score
is **0.0025**. This correct call does not establish that the Court adopted
the rationale or decided the constitutional question.

The baseline uses the prediction's frozen `elevated` band, `sal-v4`, and
Term 2025, not the evaluator's terminal context. The statpack heading
matches, establishing the `risk_set` basis. All strictly-prior rendered
Terms are pooled using their bracketed reached figures: 2024 17.9%/336,
2023 17.5%/354, 2022 19.0%/300, 2021 20.5%/342, 2020 16.1%/397,
2019 13.8%/334, 2018 15.9%/347, and 2017 17.5%/400
(rate/weighted resolved denominator). Their weighted total is 484.386
over 2,810, so **segment_base_rate = 0.172379359430605** and
**Brier skill = 0.9158663978201518**, computed as `1 - 0.0025 / rate^2`.

The rendered table covers 10 of 10 Terms; 2025 and 2026 are excluded.
There is no window shortfall. The candidate's single-Term 2024 anchor is
not the evaluator's pooled baseline. These rates are the committed pack's
rounded, denial-reweighted historical/live-slice estimates, not a live
corpus census; no corpus blob was consulted or freshness claimed.

## Reasoning quality: 0.65

The concise rationale identifies relevant adverse selection factors:
no asserted split, the state's elements/means framing, and the distinction
between two docket distributions and two fully briefed conference reviews.
It appropriately treats the response request as attention rather than
proof of a grant. Those observations give the denial forecast a coherent
basis independent of the favorable realized Brier score.

However, the reasoning discounts a single prior-Term 17.9% rate to 5%
without pooling the available prior Terms or explaining the magnitude
of the adjustment beyond the absence of a split. It omits Richardson's
specific discussion of continuous-abuse offenses and the petition's
argument about incorporation, both central in the provisioned briefs.
It also does not address the facial-challenge posture identified in the
lower opinion. Describing the issue as overriding Schad compresses the
more nuanced dispute about constitutional limits on legislative definition
of elements and means. These omissions make the analysis less complete
and its confidence harder to justify; the deductions are not for brevity
alone or for failing to retrieve additional material.

Only the rationale is assessed. The separate forecast document and the
quantitative claims do not contribute to this qualitative score. Claim
scores remain the harness's, and no semantic grades or vote accuracy are
appropriate on this cert event.

## Leakage

The log identifies forward mode but captures none of its 32 call results.
This is a visibility limitation, not proof of empty results or a candidate
fault. I evaluate the queries: provisioned files, committed base rates,
and topical searches for prior authorities, with no shown search for this
petition's disposition. The reported corpus-query failures cannot be
independently established from uncaptured results. The September 17
prediction and its treatment of the conference as pending are consistent
with an unresolved case; the supplied outcome dates denial to October 5.
There is no affirmative evidence of target-case outcome material or an
already-decided premise. Influence is `not_applicable` and leakage is not
suspected, with the capture limitation preserved explicitly.
