# Evaluation: claude-baseline

## Outcome and numerical scores

The event is an interim injunction application. It was denied on October 1, 2026, and `actual_granted` is **0**. claude-baseline's `denied` label is correct: **1**. Its **0.01** grant probability gives **(0.01 - 0)^2 = 0.0001**.

The interim baseline and Brier skill are left to the harness, with `base_rate_basis` null. The committed statpack supports the prior-Term integer counts the candidate used; I have checked a committed table, not refreshed the corpus. The candidate recognizes uneven parsing and selection differences. Those caveats matter: machine-matched substantive resolutions are not a representative class-specific rate, withdrawals/dismissals are ungranted, and mixed orders resolve denial-first. No cert salience rate belongs to this cell.

No vote accuracy is scored on an interim event. The harness owns quantitative claim scores; the forecast document is context only. Semantic grades are inapplicable.

## Reasoning quality: 0.68

The rationale correctly defines the event and frozen arrival state, acknowledges that it never read the application, and distinguishes the applicant's prior substantive application from a routine extension and the present request. It obtains potentially relevant lower-court posture rather than inferring everything from the federal-government caption. The staged retrieval metadata identifies lower-court docket lookups consistent with the described research, although it is not a substitute for full retrieved documents.

The main limitation is overgeneralization. A small, heuristically identified group of recent self-represented applicants does not substantiate an essentially-never grant rate or precisely justify a reduction to 1%. A jurisdictional dismissal is relevant but does not, without its grounds and the application, establish the prospects of reversing it. The asserted composition of the broad baseline population is not demonstrated by the table. The prior denial in an unrelated state matter has limited transferability. The rationale's abbreviated emergency-relief discussion also leaves uncertain which procedural and doctrinal route governs this affirmative injunction request.

These are limits on analysis, not penalties for predicting denial. The Court's unexplained disposition verifies the label but does not confirm the candidate's suggested reasons. The score applies only to `reasoning.md`, excluding forecast accuracy, procedural-claim calibration, and stakes judgments.

## Leakage assessment

The log is `forward` with all 32 result markers captured. Dated lower-court retrievals are earlier than the October 1 resolution. The September 23 denial of 26A397 is a different application, and its use is not this event's outcome leaking. The linked petition and lower-court research are legitimate forward context; an arrival snapshot does not forbid such retrieval while the event remains unresolved.

A broad corpus scan explicitly includes 26A434 in a filter. Its returned text is not reproduced in the staged log, and a null extracted date does not prove the result was empty. Nevertheless, the dated metadata and reasoning do not show this application's denial surfacing or being used; the rationale explicitly treats it as unresolved. I record no observed outcome retrieval or influence, not an inference that captured digests prove all results harmless.

Creation at October 1, 2026, 19:43:46 UTC is on the resolution date. Without the order's publication time, intraday ordering cannot be established. This common chronology concern is flagged. I use `influenced_prediction = none` rather than certify the forward assumption with `not_applicable`; `leakage_suspected` remains false because the available record does not affirmatively support possible outcome influence for this candidate.
