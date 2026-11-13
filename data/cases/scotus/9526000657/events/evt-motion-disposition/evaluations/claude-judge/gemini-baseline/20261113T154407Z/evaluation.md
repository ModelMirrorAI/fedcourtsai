# Evaluation — scotus/9526000657 (26A657, Schultz v. McCarthy), evt-motion-disposition — gemini-baseline

**Outcome.** Interim cell (a stay application). The Chief Justice denied the application on 2026-11-10, eight days after its Nov 2 submission, with no response requested, no referral to the Court, no amicus filings and no writing. `outcome.json` records `interim_reading: denied`, `interim_granted: 0`.

**Scores.** Predicted `denied` at probability 0.005: `correct` = 1 (same side of the granted/ungranted line), `brier_score` = 0.000025. The baseline and skill are the harness's on an interim cell; `segment_base_rate`, `brier_skill_score` and `base_rate_basis` are left null for the stamp, as are `claim_scores`. No `vote_accuracy` (not a merits cell) and no `semantic_grades` (no semantic set on an interim cell). The prediction's `context.band` is null, the ordinary interim shape.

**Base-rate build.** The candidate recorded statpack digest sha256:b122cc43…; `statpack-at` resolved it to build f0a8cabd41e6 (landed 2026-11-07, no alternative), and base-rate use is graded against that build rather than the committed pack. In it, the interim pool an OT2026 application reads is 156/1337 over OT2016–OT2025 and the private/unmarked cell is 63/906.

## Reasoning (`reasoning_quality` 0.6)

This rationale has the best case-specific work of the cell and the worst base-rate work, and the grade reflects both.

On the case: with the application text unreadable, it found the Fourth Circuit docket (No. 26-2406), read the Oct. 26 unpublished per curiam denying mandamus to disqualify the district judge in the applicant's bankruptcy appeal, and placed it among parallel mandamus denials and a companion application (26A658). The application text now in the record confirms that posture (a stay sought while rehearing on the recusal question was pending — the pending rehearing petition is the one piece it did not mention). Applying the stay standard to an unpublished recusal-mandamus denial with no split is the right analysis, and it supports a very low number.

On the anchor: the figures it quotes do not appear in the statpack build it recorded. It says the strictly-prior pool holds only OT2025 at 30/148 = 20.3%, with a private/unmarked cell of 9/92, federal 17/22, state 2/5, and signal counts over a 231-application slice. The build has the pool at 156/1337 over OT2016–OT2025 and private/unmarked at 63/906; none of the quoted counts is there. It also asserts that the nine private grants "occurred in represented cases" that drew a response and referral, which nothing in the pack or its logged retrieval supports. The error did not move the final number, which was driven by the case-specific adjustment, but a rationale that presents unverifiable figures as read from the pack is unsound on that limb. The claim that the unreadable application creates "negligible uncertainty" is also stronger than a 61-page unread filing warrants, though 0.5% is not unreasonable for this posture.

## Predicted reasoning (`predicted_reasoning_quality` 0.9)

Central claims: the Chief Justice denies in chambers by summary order with no writing; within two to ten days of submission; no response called for; no referral; and the ground — failure of the stay standard on a recusal-mandamus denial. The first four are borne out, and they are the most specific commitments in the cell: the actor, a tight window that the eight-day denial fell inside, and near-certain no-response and no-referral calls. The ground cannot be settled from an unexplained order and is marked unresolved; the "if the Court ever reached the merits" passage is conditional and earns nothing either way. Just short of the top anchor because the one substantive claim is unresolvable on this record.

## Leakage

Forward; prediction written the day before the denial. The log is mostly `outcome_only`, so it is graded on queries: neighbouring application numbers (including the applicant's companion application) and the lower-court dockets and opinions, all dated before the prediction. None reaches for this application's disposition, and the reasoning cites nothing later than Nov 9. `not_applicable`, not suspected.
