# Evaluation: codex-baseline

## Outcome and numerical score

This cert-stage event resolved as `denied` on October 13, 2026, with
`actual_granted = 0`. codex-baseline predicted `denied` with grant probability
0.16. Exact-label correctness is **1** and the Brier score is
**(0.16 - 0)^2 = 0.0256**.

The scored prediction freezes `high` under `sal-v4`, Term 2025. The stamped
segment base rate, basis, and Brier skill belong to the harness and are not
supplied independently here. Cert votes are unscored. No semantic set applies;
mechanical claim scores and the forecast document are outside this grade.

## Reasoning quality: 0.94

The analysis identifies the strongest review-favoring fact, an acknowledged
surcharge conflict, without confusing it with a reason this particular
petition must be granted. It accurately states the government's actual
recommendation and its distinction between broad doctrinal disagreement and
vehicle fitness. The staged United States brief, printed pages 8-9 and 15-18,
supports the top-hat-plan exception, unresolved fiduciary status, lack of a
demonstrated conflict in this particular setting, and the vacated Fifth
Circuit panel decision. The separate weakness of the preemption question is
also recognized.

The rationale engages with the petitioners' answer that the categorical
remedial issue could be decided while leaving status and liability for remand.
It treats briefing as advocacy, identifies which supporting lower-court
characterizations were not independently checked, and does not turn a
plan-specific objection into a categorical conclusion that petitioners can
never recover. This yields a clear explanation for both the downward
adjustment and the remaining possibility of review.

Its statistical reasoning is particularly careful about reference populations:
the stated anchor uses the frozen band and prior Terms; the CVSG and
distribution signals are not counted again as independent multipliers; and
terminal relist buckets are not treated as forward hazards. It explicitly
labels the final probability a judgmental adjustment rather than inventing a
measured SG-denial conditional rate. I have not independently reconstructed
the historical pack or treated its displayed-window calculation as the
harness's final stamped anchor.

The residual limitation is calibration: the evidence supports a downward
adjustment but does not empirically identify 16% as the correct magnitude.
Some counterarguments rely on the parties' accounts rather than independent
lower-court verification. These disclosed limitations keep the score below
perfect. The higher grade reflects analytical discipline, not simply a lower
Brier score or success on ancillary forecasts.

An unexplained denial does not establish the Court's internal rationale or
resolve the surcharge question. codex-baseline expressly preserves that
distinction. Only `reasoning.md` is graded; no score is assigned to the
forecast prose or structured claims.

## Leakage and significance

The transcript places the calls on September 18, before resolution. The two
unobserved web-class calls identify the exact August 31 SG PDF; I do not
infer failure or absence of content from those markers. The remaining 27
calls are captured, including subsequent extraction of that brief and the
September 16 supplemental submission. Their subjects and the rationale concern
predecision advocacy, not the Court's eventual denial. Collapsed `other` tool
labels are not evidence of misconduct. No outcome-revealing retrieval is
shown, so the forward assessment is `not_applicable` and
`leakage_suspected = false`.

The independent stakes score is 0.55: the QP raises a potentially important
national ERISA remedy question, but the specialized vehicle limits its reach
and the actual denial establishes no merits rule.
