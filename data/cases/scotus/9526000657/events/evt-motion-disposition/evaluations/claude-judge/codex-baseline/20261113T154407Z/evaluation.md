# Evaluation — scotus/9526000657 (26A657, Schultz v. McCarthy), evt-motion-disposition — codex-baseline

**Outcome.** Interim cell (a stay application). The Chief Justice denied the application on 2026-11-10, eight days after its Nov 2 submission, with no response requested, no referral to the Court, no amicus filings and no writing. `outcome.json` records `interim_reading: denied`, `interim_granted: 0`.

**Scores.** Predicted `denied` at probability 0.07: `correct` = 1 (same side of the granted/ungranted line), `brier_score` = 0.0049. The baseline and skill are the harness's on an interim cell; `segment_base_rate`, `brier_skill_score` and `base_rate_basis` are left null for the stamp, as are `claim_scores`. No `vote_accuracy` (not a merits cell) and no `semantic_grades` (no semantic set on an interim cell). The prediction's `context.band` is null, the ordinary interim shape.

**Base-rate build.** The candidate recorded statpack digest sha256:b122cc43…; `statpack-at` resolved it to build f0a8cabd41e6 (landed 2026-11-07, no alternative), and base-rate use is graded against that build rather than the committed pack. In it, the interim pool an OT2026 application reads is 156/1337 over OT2016–OT2025 and the private/unmarked cell is 63/906.

## Reasoning (`reasoning_quality` 0.68)

The rationale is careful and its numbers are right: it pooled OT2016–OT2025 Term by Term to 156/1337, used the private/unmarked cell (63/906), and correctly noted the uneven parse coverage and that the ladder counts are right-censored and not arrival-conditioned. Its handling of the blank application is disciplined, and it was honest that its lower-court search returned nothing.

What holds it back is that it stopped at the class rate. It recognised the applicant as self-represented and declined to adjust for it because the penalty was "unmeasured". That is defensible as method, but it leaves 7% as the answer for an unrepresented individual's application in a private dispute with no escalation signal — a population any experienced reader would place well below the cell that includes represented, organized applicants. The 30% referral and 12% response figures are likewise high for this posture, and are stated to be judgmental. It also did not locate the Fourth Circuit proceeding, so the forecast carries no case-specific content. Sound and well calibrated to what it allowed itself to use; less informative than it could have been.

## Predicted reasoning (`predicted_reasoning_quality` 0.6)

Central claims: denial by a short unexplained order; probably no response; probably no referral; disposition about Nov 9–23 with no writing; no amici. All are borne out. But the document commits to little beyond the outcome: "the Court or the Chief Justice" leaves open who acts, the signal claims are probabilistic restatements of the claims block, and it expressly forecasts no ground. The dated window and the no-writing call are its only specific commitments, and the window is wide. Right in direction and generic, so just above the 0.5 anchor.

## Leakage

Forward; prediction written the day before the denial. The web calls went to the Court's general rules pages, not this docket, and the one CourtListener search was for the lower-court docket filed before Nov 3. Nothing resolving this application surfaced. `not_applicable`, not suspected.
