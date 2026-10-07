# Evaluation: claude-baseline

## Outcome and quantitative score

The cert-stage outcome is `denied`, resolved October 5, 2026, with
`actual_granted = 0`. claude-baseline's `denied` label is correct (**1**), and
its probability of 0.20 produces `(0.20 - 0)^2 = 0.04`.

The outcome records a single distribution and a noted dissent from denial;
the provisioned snapshot identifies Justice Kavanaugh as willing to grant.
Those facts do not create a cert vote-accuracy score. No merits judgment or
semantic set is present. The forecast document and quantitative claims are
not graded here; the harness owns mechanical claim scoring, and neither
forecast timing nor a claim's realized result enters reasoning quality.

## Baseline unavailable under the frozen version

claude-baseline freezes band `baseline`, version `sal-v3`, and Term 2026. The
available segment table in `metrics/statpack.md` uses **sal-v4**, not sal-v3.
Although its caption renders all 10 Terms and OT2017-OT2025 are strictly prior,
those populations cannot serve as this prediction's frozen-version baseline.
`segment_base_rate` and `brier_skill_score` are omitted; `base_rate_basis` is
null. A terminal fallback is impermissible for a prediction with a frozen band.
The mismatch is recorded in the shared flags file.

The rationale's claimed historical pooled anchor of about 6.5% is therefore
not independently verified from the current table. The analysis clearly states
its intended risk-set population, prior-Term window, and weighting; the later
version mismatch is not a mark against that method or the predictor.

## Reasoning quality: 0.80

The probability rationale is explicit and balanced. It separates a claimed
conflict from a proven split, considers fact-specific application and vehicle
objections, and treats the absent BIO as an important information gap. Its
discussion of Detwiler distinguishes an unconfirmed Supreme Court docket from
the existence of the lower-court litigation and recognizes possible coverage
lag. These qualifications support a denial-first forecast despite plausible
reasons to raise the probability above its stated prior.

There are identifiable limitations. The rationale calls Judge Willett a
"dissenting-in-part" judge, whereas the provisioned petition describes him as
concurring in part and in the judgment, joining the result under an
abuse-of-discretion standard. His objections still matter, but overlooking
that distinction overstates the separate writing's grant signal. Counsel,
business interest, the suggested religious-liberty/class-action cross-currents,
and supposed appetite following another case supply qualitative judgments,
not an empirically demonstrated threefold uplift. Comparing the arrival
forecast to petitions that eventually reach an elevated band is also only
an analogy, not evidence of this petition's own future trajectory. The
rationale appropriately admits part of that uncertainty.

The score assesses the quality of the analysis in `reasoning.md`, not the
Court's unstated reasons for denial and not whether the ancillary forecasts
came true.

## Leakage

The log says `forward`; the prediction was made August 16, before the recorded
October 5 denial. Result-capture coverage is 1.0. The external calls visible
in the log concern prior granted petitions and Detwiler, with extracted dates
of September 3 and September 23, 2025; neither identifies this petition's
disposition. The reasoning treats the response and decision as outstanding.

Capture coverage establishes recorded results, not that every result body is
available in this staged digest log. Nothing in the visible queries, dates,
or prose indicates a decided case was mis-provisioned forward. The assessment
is `retrieved_outcome_material = false`, influence `not_applicable`, and
`leakage_suspected = false`.
