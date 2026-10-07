# Evaluation: gemini-baseline

## Outcome and quantitative score

This is a cert-stage arrival prediction. The provisioned outcome records denial
on October 5, 2026, with `actual_granted = 0`. gemini-baseline predicted `denied`,
so exact-label correctness is **1**. Its grant-family probability was 0.28:
`(0.28 - 0)^2 = 0.0784`.

The outcome also records one distribution and a noted dissent from denial. The
October 5 snapshot states that Justice Kavanaugh would grant. These are context,
not grounds for assigning per-Justice accuracy: cert votes are not scored.
There is no merits judgment or declared semantic set to grade. Quantitative
claims remain exclusively for the harness; the forecast document was read for
context and was not scored.

## Baseline unavailable under the frozen version

The prediction freezes `baseline`, `sal-v3`, and Term 2026. The committed
`metrics/statpack.md` segment table is headed **sal-v4**. Its caption renders
10 of 10 Terms, with OT2017-OT2025 strictly preceding this case's Term, but
those rows do not define the frozen sal-v3 population. Accordingly,
`segment_base_rate` and `brier_skill_score` are omitted and `base_rate_basis`
is null. Neither the terminal-band fallback nor the evaluator's decided-docket
context can repair that mismatch. The shared flags file records it.

This mismatch is not attributed to the predictor as a forecasting error. Its
historical 5.4% anchor cannot be independently reconstructed from the current
version-mismatched table. Its rationale nevertheless identifies only OT2025
rather than explaining a resolved-weighted pool of all eligible rendered Terms.

## Reasoning quality: 0.65

The rationale recognizes relevant petition-specific reasons to move above an
arrival prior: the asserted Rule 23 conflict, experienced counsel, and the
alternative Detwiler hold/GVR route. It keeps denial more likely than a grant
and identifies a plausible reason the Court might prefer another vehicle.

The upward move to 28% is weakly calibrated. The analysis largely accepts the
petition's conflict framing without testing whether the cited decisions present
a square rule conflict rather than different applications. It does not engage
the petition's account that Judge Willett joined the judgment under a deferential
standard, or explain how interlocutory posture and the missing opposition
affect the estimate. Anticipated business interest and a generalized account of
the Justices' preferences do substantial work without a demonstrated numerical
link. Detwiler is treated as a strong potential GVR path without enough attention
to the successive contingencies of review, a relevant ruling, and its effect
here. These are weaknesses of the probability rationale, not penalties for
unrealized forecasts or a deduction merely because review was denied.

## Leakage

The captured log labels this a forward prediction. The August 16 prediction
precedes the October 5 resolution; the visible searches concern class
certification and Detwiler, and the prose treats this petition as pending.
Nothing visible identifies its eventual denial as already known.

All result markers are `unobserved` (coverage 0.0). In particular, null dates
on web-search rows do not establish that searches returned nothing. The
assessment uses the recorded timing, query subjects, and prose, with that
visibility limitation. Ordinary retrieval about a genuinely pending petition
was permitted: `retrieved_outcome_material = false`, influence
`not_applicable`, and `leakage_suspected = false`.
