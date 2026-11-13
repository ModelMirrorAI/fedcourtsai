# Evaluation — scotus/9526000657 (26A657, Schultz v. McCarthy), evt-motion-disposition — claude-baseline

**Outcome.** Interim cell (a stay application). The Chief Justice denied the application on 2026-11-10, eight days after its Nov 2 submission, with no response requested, no referral to the Court, no amicus filings and no writing. `outcome.json` records `interim_reading: denied`, `interim_granted: 0`.

**Scores.** Predicted `denied` at probability 0.015: `correct` = 1 (same side of the granted/ungranted line), `brier_score` = 0.000225. The baseline and skill are the harness's on an interim cell; `segment_base_rate`, `brier_skill_score` and `base_rate_basis` are left null for the stamp, as are `claim_scores`. No `vote_accuracy` (not a merits cell) and no `semantic_grades` (no semantic set on an interim cell). The prediction's `context.band` is null, the ordinary interim shape.

**Base-rate build.** The candidate recorded statpack digest sha256:b122cc43…; `statpack-at` resolved it to build f0a8cabd41e6 (landed 2026-11-07, no alternative), and base-rate use is graded against that build rather than the committed pack. In it, the interim pool an OT2026 application reads is 156/1337 over OT2016–OT2025 and the private/unmarked cell is 63/906.

## Reasoning (`reasoning_quality` 0.82)

The rationale is sound and well proportioned. It read the pool correctly (156/1337, every pooled Term with `finer_unread` 0) and the private/unmarked cell (63/906), then explained why that cell overstates this applicant's chances: it mixes in represented, organized litigants, and a pro se individual in a private dispute sits far below it. The move from 7% to 1.5% is a judgment call rather than a measured rate, but it is stated as one and it points the right way.

With the application text unreadable, it used CourtListener to infer a pro se debtor's serial bankruptcy litigation against a trustee, and labelled that an unconfirmed inference the forecast does not hinge on. The application text now in the record confirms it. It kept the probability off the floor expressly because the application could not be read, which is the right use of residual uncertainty.

Weaker points: the 15% referral figure rests on a renewal-to-another-Justice route that is real but was asserted rather than sourced, and it did not find the Fourth Circuit mandamus ruling itself, so the posture stayed at the level of inference.

## Predicted reasoning (`predicted_reasoning_quality` 0.8)

Central claims: denial by the Chief Justice as Circuit Justice in an unexplained order with no writing; no call for a response; no referral on this application; timing of one to three weeks; no amici. All five are borne out by the docket and `interim_signals`. Naming the Chief Justice as the actor, and saying a referral would come only by renewal, are commitments a reader could have got wrong. It sits below the top anchor because the timing window is wide (the denial landed at its early edge) and the stated ground is generic — no fair prospect of certiorari, no irreparable harm — without the case's actual posture. The conditional "if somehow granted" line earns nothing either way.

## Leakage

Forward; prediction written the day before the denial. The log's latest document date is Nov 6, and the live docket fetch on Nov 9 showed only the submission entry, which the reasoning discloses. `not_applicable`, not suspected.
