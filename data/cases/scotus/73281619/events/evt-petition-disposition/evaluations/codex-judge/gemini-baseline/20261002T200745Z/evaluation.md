# Evaluation: gemini-baseline

## Outcome and quantitative score

This is a cert-stage evaluation of the blinded prediction from run
`20260918T174135Z`. The supplied outcome records `granted`, `actual_granted = 1`,
and a plenary route, resolved October 1, 2026. The provisioned October 1 snapshot
specifies that the grant was limited to Question 1. The predicted disposition
was `denied`, so exact-label correctness is **0**. With P(grant) = 0.05, the
Brier score is **(0.05 - 1)^2 = 0.9025**. A limited-question grant is still a
grant on this event's recorded axis.

## Baseline

The prediction froze Term 2025, band `elevated`, and `salience_version = sal-v4`.
The committed `metrics/statpack.md` heading matches that version. I use its
bracketed elevated **reached** rates, not terminal rates and not the evaluator's
decided-docket context. The table renders all 10 of its 10 Terms, 2017–2026;
the strictly-prior window for this prediction is 2017–2024.

The rendered percentage/weighted-resolved pairs are 2017: 17.5%/400;
2018: 15.9%/347; 2019: 13.8%/334; 2020: 16.1%/397; 2021: 20.5%/342;
2022: 19.0%/300; 2023: 17.5%/354; 2024: 17.9%/336. Resolved-weighted
pooling gives **484.386 / 2,810 = 0.172379359430605**, on the `risk_set` basis.
The numerator is reconstructed from rounded printed percentages, not an exact
grant count. These are the committed pack's denial-reweighted live/historical
slice estimates, not a fresh corpus measurement. No corpus was queried.

The baseline Brier is 0.6849559246964957; skill is
**1 - 0.9025 / 0.6849559246964957 = -0.3176030273771238**.
Thus this realized prediction does worse than that baseline. One resolved
event does not establish population calibration or comparative performance.

## Reasoning quality: 0.50

The analysis identifies substantive questions under RLUIPA and two concrete
vehicle objections rather than simply applying an overall denial rate. The
invited-error objection is grounded in the opposition's discussion at printed
pages 27–28; the late-raised equal-terms claim and comparator-record objection
appear at pages 35–36. Starting from approximately the appropriate band rate
and considering these objections is a sensible analytical structure.

The sharp reduction to 5%, however, is insufficiently defended. Calling the
vehicle problems fatal gives an opponent's disputed characterization too much
weight without examining the petition's answer or separating the substantial-
burden question from the equal-terms question. The petition at page 36 disputes
the latter account, describing a legal question addressed below. A defect
particular to Question 2 need not defeat review of Question 1; the eventual
limited grant illustrates that distinction, without establishing the Court's
reasons for granting or resolving the objections on their merits.

The reasoning also equates two distributions with an ordinary first relist.
The provisioned chronology instead shows a May 12 distribution, a May 14
response request after waiver, and a September 2 distribution after briefing.
That sequence does not establish an unexplained post-briefing relist. The
analysis neither addresses the response request nor meaningfully weighs the
recorded amicus participation. Its asserted 15–25% relist/counsel range has no
identified matched denominator. These are limitations of the analysis itself,
not a penalty imposed merely because a low-probability grant occurred.

## Leakage and scope

The captured log labels the prediction forward. Its September 18 creation and
logged activity predate the October 1 resolution. All 35 calls have
`result_capture = unobserved` and coverage is 0.0. I assessed their query scope
without interpreting missing result dates or digests as proof of no retrieval.
The visible calls read local instructions, briefs and aggregate statistics,
write outputs, and validate. No visible query seeks the petition's disposition,
and the rationale and retrieval note contain no evidence of knowing it.
Accordingly, outcome material is not shown as retrieved, influence is
`not_applicable`, and `leakage_suspected` is false. Capture incompleteness limits
that conclusion but does not itself establish leakage or a tooling defect.

The forecast document was read for context only. Neither it nor the structured
quantitative claims contributes to reasoning quality. Claim scores are left
to the harness. No vote accuracy or semantic grades are written on this cert
cell. The optional independent stakes assessment is omitted.
