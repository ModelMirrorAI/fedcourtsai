# Evaluation: claude-baseline

## Outcome and scores

This is an **interim / arrival** stay application. The supplied outcome
records denial on October 5, 2026, with `actual_granted = 0`.
claude-baseline predicted `denied` on October 3, so `correct = 1`.
P(grant) = 0.01 yields `brier_score = (0.01 - 0)^2 = 0.0001`.

A correct disposition does not validate the rationale's characterizations of
the underlying dispute. The supplied outcome contains no substantive
explanation establishing those characterizations.

## Reasoning quality: 0.56

The rationale correctly identifies the interim posture and arrival boundary,
uses the prior-Term substantive application pool, and explains uneven parse
coverage. It acknowledges the unread application and unsuccessful attempts
to examine background dockets. It identifies a demanding stay showing
rather than confusing the application with the ultimate merits judgment.
Its distinction between background litigation history and the unknown Texas
judgment is useful.

Several later assertions exceed those limits. The statpack's published
counts do not establish that its cohort is dominated by counseled or
governmental applicants, or that grants go to institutional applicants with
contested equities. The two recent denials cited are too few and too weakly
matched to identify this applicant's grant probability. No escalation at the
opening entry is not equivalent to a later failure to attract Court
attention. General litigation-history results do not establish the federal
question or harm presented by the unread application.

The clearest overstatement is the assertion that nothing in the unread
materials could plausibly raise the chance above a few percent. That removes
uncertainty the candidate has just established rather than explaining it.
The residual probability is framed substantially as order-entry or resolver
noise, with little allowance for a substantive reason to grant relief that
the missing filing might supply. The denial call is plausible, but the
specific 1% probability is more confident than the documented case-specific
evidence warrants. The quality score gives credit for the explicit baseline
and limitations while discounting these unsupported inferences; it is not
a reward for the small realized Brier error.

This grade is confined to `reasoning.md`. I read the separate forecast for
context but do not score its timing, predicted procedural path, or the
structured claims. Those forecasts do not augment the quality grade.

## Baseline and exclusions

Interim baseline and skill are computed by the harness; neither is written
in this evaluation JSON, and `base_rate_basis` is null. The prediction's
frozen application Term is 2026 and its band is null. The committed pack
contains the interim section and prior-Term resolved substantive counts:
70 in 2024 with 14 grants, and 226 in 2025 with 17 grants. Earlier eligible
rows contribute no parsed resolutions. The pool clears the 50-resolution
floor, so neither a missing-section nor a thin-pool refusal is apparent.
The harness stamp remains to be executed. These are committed-pack counts,
not a fresh corpus measurement; uneven parsing and the selected prediction
population limit interpretation. Current-Term observations may be forward
context, but are not part of the scoring baseline.

No vote accuracy is allowed on this stage. No semantic set is declared and
no semantic grades are written. Mechanical claim scores remain entirely
the harness's. I omit the optional independent stakes assessment.

## Leakage and input limits

The log records forward mode and 31/31 captured call results. Its party,
lower-court, and application-docket searches were on October 3, before the
October 5 denial. The log also shows current-Term corpus retrieval and
consultation of predictions for other applications, which the candidate's
retrieval note does not fully enumerate. I assess those visible calls rather
than relying exclusively on the self-report. None of their query slices,
extracted dates, or the candidate's rationale demonstrates this application's
own disposition as already known. The background endpoint attempts have
throttled/error statuses. Captured hashes are not the returned source texts,
so they do not allow independent verification of every background assertion.

Outcome retrieval is assessed false, influence not applicable, and leakage
suspected false. Party-history searches, other cases' outcomes, and material
after the frozen September 28 baseline are not automatically leakage in an
open forward cell. The arrival-position boundary is not applied as a replay
retrieval prohibition here.

The candidate reports blank application text. The evaluator's current
manifest instead marks the 44-page application OCR-derived and nonempty;
its current text file is 50,786 bytes. I inspected only the metadata and
size, not that body. This cannot establish the candidate's earlier document
availability, and the reported extraction gap itself receives no penalty.
The cell-level flags record that provenance limitation.
