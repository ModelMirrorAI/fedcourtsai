# Evaluation: gemini-baseline

## Outcome and quantitative scores

This is a cert-stage cell. The supplied outcome records denial on October 5,
2026, with `actual_granted = 0`. The candidate predicted `denied` with grant
probability 0.07: exact-label correctness is 1 and Brier loss is
`(0.07 - 0)^2 = 0.0049`. A correct denial does not establish that the Court
adopted the candidate's explanation; the outcome provides no reasons.

The prediction froze Term 2025, band `elevated`, and version `sal-v4`.
The committed statpack's matching table renders all 10 of its 10 Terms. Pooling
only the bracketed reached figures for 2017-2024 gives a weighted denominator
of 2,810 and a rounded-rate numerator of 484.386: baseline
`484.386 / 2810 = 0.172379359430605`. The rate/weight pairs, in ascending Term
order, are 17.5%/400, 15.9%/347, 13.8%/334, 16.1%/397, 20.5%/342,
19.0%/300, 17.5%/354, and 17.9%/336. Terms 2025 and 2026 are excluded.
These are denial-reweighted live/historical-slice estimates, not exact grant
counts. Display rounding limits precision. This is the committed reference
pack, not a freshly queried corpus estimate; no pack build timestamp is supplied
in the inspected table. The basis is `risk_set`, not the leading terminal rate
or this evaluator's terminal context. Skill is
`1 - 0.0049 / baseline^2 = 0.8350981397274976`.

## Reasoning quality: 0.70

The rationale identifies relevant reasons to discount a grant: a claimed
conflict built partly on dicta or other statutory settings, the breadth of the
question, and the opposition's preservation objection. Those points are
grounded in the provisioned BIO's split and vehicle discussions and the
appellate opinion reproduced at petition App. 9a-10a. It also recognizes the
response request and municipal amicus support as countervailing attention
signals. The low grant probability is intelligible rather than merely a
denial-base-rate guess.

The explanation is nonetheless compressed and accepts the BIO's split framing
without distinguishing the Fourth Circuit's potentially meaningful difference
in approach from the Tenth Circuit's discretionary holding. Its suggestion
about what spurred the response request is speculative. More concretely, its
13.5% anchor comes from the case's own Term 2025 rather than the required
strictly-prior pool of about 17.24%. That is a baseline-selection weakness, not
evidence of exposure to the eventual denial. The movement from the selected
anchor to 7% is judgmental and only briefly explained. These limitations, not
the already-known result, determine the quality grade.

## Leakage assessment

The harness log records forward mode and September 17 calls, before the
October 5 disposition. Its queries and the rationale do not reveal this case's
resolved outcome. All 29 call results are unobserved: neither null document
dates nor null digests establish that any lookup returned nothing. The query
at index 18 attempts a general corpus lookup for denied SCOTUS cases with
`--decided-before "2026-09-17"`. Its outcome cannot be recovered from the log;
I do not assume success, failure, or returned cases. This differs from the
candidate's statement that it made no retrieval beyond provisioned inputs and
is noted in the cell flags. It does not establish outcome leakage. The grade
is `not_applicable`, with `leakage_suspected = false`.

Only `reasoning.md` receives the qualitative grade. The forecast document was
read for context, not scored. Quantitative claims remain for the harness; no
semantic grades or cert-vote score are written. The optional independent
big-case assessment is omitted.
