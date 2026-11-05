# Evaluation of claude-baseline

**Cell:** scotus/9526000619 · evt-motion-disposition · **interim** stage (application 26A619, a stay of a Maryland writ of possession, submitted to the Chief Justice on Oct 27, 2026).
**Outcome:** denied by The Chief Justice on Nov 3, 2026 (`interim_reading` denied, `interim_granted` 0); no response requested, no referral, no amici.

**Scoring.** The outcome records the finer interim reading, so the cell is scored on `interim_granted` = 0. A `denied` prediction falls on the ungranted side, so `correct` = 1. `brier_score` = p². This is an interim cell, so the segment base rate and the skill score come from the harness stamp (pooled from the interim slice over application Terms before 2026) and I wrote neither. Every candidate reports that the committed pack's finer-reading pool for 2016–2025 has zero resolved applications. If that holds, the stamp will come back null because the pool is below its floor and unread rows remain, not because the section is missing. No vote accuracy is scored on this stage, and no semantic set is declared.

**Leakage.** The log's mode is forward. The Nov 3 denial came on the same date the predictions were made (~22:4xZ), so I did not pass the cell by default. I checked each log for this case's own disposition (see the note below and flags.json).

## claude-baseline: p = 0.02, denied → correct 1, Brier 0.0004

**Reasoning (0.70).** Concise and sound. It correctly finds the finer-reading pool unusable and anchors without it. It uses the older substantive rate only for shape, and correctly notes that government, capital and represented applicants account for most grants. It reasons from the pro se applicant, the private respondent and the state-court origin to an in-chambers denial, and it is candid about the unread filing ("discount me where"). Like codex-baseline, it did not research the underlying dispute. It names foreclosure as a guess without using it, which keeps the number broader than the record supported. The 12% referral figure rests on a plausible renewal-to-a-second-Justice route.

**Leakage.** At 22:40Z on Nov 3 the candidate fetched this application's own live supremecourt.gov docket page. That date is the resolution date, and the denial is entered on the docket for that day. The result was captured but I cannot read its content. The candidate discloses that the page showed only the Oct 27 entry, consistent with the order not yet having posted. Nothing in the reasoning presupposes the denial, and the forecast of a possible renewal and referral is the shape of an open case. I grade retrieved_outcome_material false and influence none, relying on that disclosure. A captured fetch of the case's own docket on its resolution date is the one item a maintainer should check, and it is flagged.

## Predicted reasoning (0.70)

Central claims: (1) the Chief Justice, acting alone, denies within about two weeks without a response; (2) no initial referral, with renewal as the route to one; (3) no amici and a one-line order; (4) any grant would be an administrative stay. Claims 1 and 3 were borne out, and the referral half of claim 2 was borne out as of disposition. The renewal path and claim 4 are conditional and untested. The document is specific but stays on the modal path, as codex-baseline does.
