# Evaluation: codex-baseline, Guardado v. Florida (26A623), evt-motion-disposition

## Cell
Interim cell (`stage: interim`): application 26A623, a capital stay of execution pending the linked cert petition 26-6013. The outcome records the finer interim reading (`interim_reading: denied`, `interim_granted: 0`). On Nov 5, 2026 the application was referred to the Court and denied, in the same order that denied certiorari. No separate writing is noted. Florida filed its response on Nov 2 without a docketed call for one. No amicus filed.

The baseline (`segment_base_rate`) and `brier_skill_score` belong to the harness: `stamp-cell` pools the interim substantive grant rate over prior application-Terms. I left both null and quote no rate of my own. The candidates report that the committed statpack carries no finer-reading counts for 2016-2025 (`finer_resolved` 0, `finer_unread` > 0). If that holds, the stamped rate should come back null because the pool falls below its registered floor and fails the zero-unread condition. I did not re-read the statpack to confirm this. `vote_accuracy` is omitted because this is not a merits cell. There are no `semantic_grades` (no declared semantic set on an interim cell). No band was frozen, so no flag is needed.

## Leakage
Forward mode. The prediction was made Nov 4, 2026, before the Nov 5 resolution. Nothing in the log or prose retrieves or presupposes this application's disposition. Graded `not_applicable`, `leakage_suspected: false`.

The log is 92% captured. It covers local reads, corpus queries (unrelated cert denials, and a Woodard citation lookup that returned no rows), and a CourtListener read of the 1998 Woodard concurrence. It also shows two unobserved web searches. I graded those on their queries, which concern historical Woodard and Barefoot authority only.

## Score
P(grant) = 0.03 and the predicted label is `denied`, against `interim_granted` 0. So `correct` = 1 and Brier = 0.0009.

## Reasoning quality: 0.7
The legal analysis of the Woodard concurrence is careful and accurate. It distinguishes an adverse exercise of executive discretion from a denial of access to the clemency process, and it fairly flags the categorical-policy allegation as the applicant's best argument. It correctly declines a substitute baseline. However, it did not look for the Florida Supreme Court opinion or any recent Florida warrant comparator. It treats the missing state-court reasoning as irreducible uncertainty when it was retrievable. That is the main reason the 3% is somewhat less tightly grounded than it could have been. The procedural forecasts in the same document (a 70% chance of a response request) are outside this grade.

## Predicted reasoning: 0.65
Borne out: the disposition, timing in the final two days before the execution, referral, no amicus, and no separate writing. The one specific procedural call that departed from the ordinary pattern failed: a docketed response request was rated "more likely than not," but Florida responded unprompted and no request was entered. The document's stated ground for the denial is unresolved, because the order is unexplained. The result is a correct direction with one failed secondary claim and otherwise generic content.
