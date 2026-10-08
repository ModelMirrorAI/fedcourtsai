# Evaluation: gemini-baseline

## Outcome and scores

This is an **interim / arrival** application, not a cert or merits decision.
The supplied outcome records denial on October 5, 2026, with
`actual_granted = 0`. gemini-baseline's October 3 prediction names `denied`, so
`correct = 1`; its grant probability of 0.001 gives
`brier_score = (0.001 - 0)^2 = 0.000001`.

The realized denial establishes the label, not the Court's reasons. The record
does not establish that the Court found the underlying claims frivolous or
adopted the candidate's explanation.

## Reasoning quality: 0.40

The rationale identifies the application posture, uses the appropriate interim
baseline rather than a cert band, and acknowledges that the application text
was unavailable. A denial forecast is intelligible from its stated prior and
limited docket information. These are substantive strengths independent of
the successful outcome.

The main weakness is the jump from sparse information to near-certainty. The
document characterizes the underlying claims as apparently frivolous and
asserts that extraordinary circumstances are absent while also admitting that
the application could not be read. Its claim that this class of pro se
applications is uniformly denied is unsupported by a measured subgroup or a
documented case-specific analysis. The reported litigation-history search is
not a substitute for examining the application at issue. A corpus query
restricted to denials cannot estimate that subgroup's grant rate. The
rationale does not adequately justify reducing the baseline to 0.1% or retain
uncertainty about an unread filing. The low Brier error does not repair those
evidentiary gaps.

This score grades only `reasoning.md`. I read `predicted_reasoning.md` for
context but do not score its forecast, timing, or the structured claims.

## Baseline and exclusions

The interim baseline and Brier skill are harness-owned and are deliberately
absent from this JSON; `base_rate_basis` is null. The frozen application Term
is 2026 and the band is null. The committed statpack has an interim section:
its prior-Term rows include 70 resolved substantive applications in 2024 and
226 in 2025, with 14 and 17 grants respectively. Earlier rows in the ten-Term
window add no parsed resolutions. This supports the candidate's cited anchor
and clears the 50-resolution floor; no missing-section or thin-pool refusal
is apparent. This is a reading of the committed pack, not a fresh corpus
estimate or a report of a stamp already executed. Parse coverage and
prediction-selection caveats still apply.

Votes are not scored at the interim stage. No semantic set is declared, and
no semantic grades or harness-computed claim scores are written. I omit the
optional independent stakes assessment.

## Leakage and input limits

The captured log identifies forward mode. All calls occurred October 3,
before the supplied October 5 resolution. The parties search and corpus
query do not show this application already decided; the prose does not
presuppose its actual disposition. Thus outcome retrieval is assessed false,
influence not applicable, and leakage suspected false. Result capture is
0/22: returned contents cannot be independently inspected from this log.
Null dates do not mean the searches returned nothing, and the candidate
expressly reports obtaining background litigation information. Forward
retrieval after the September 28 baseline cutoff is not itself leakage.

The candidate reports blank application text. The evaluator's current
document manifest instead reports OCR-derived, nonempty text, and the current
file is 50,786 bytes. That later input state does not establish what the
candidate could read. I do not penalize the reported extraction failure or
use the current application's body to reconstruct its evidence. The
provenance limitation is recorded in the cell-level flags.
