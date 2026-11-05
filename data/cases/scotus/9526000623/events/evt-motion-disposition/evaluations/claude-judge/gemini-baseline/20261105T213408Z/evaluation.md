# Evaluation: gemini-baseline, Guardado v. Florida (26A623), evt-motion-disposition

## Cell
Interim cell (`stage: interim`): application 26A623, a capital stay of execution pending the linked cert petition 26-6013. The outcome records the finer interim reading (`interim_reading: denied`, `interim_granted: 0`). On Nov 5, 2026 the application was referred to the Court and denied, in the same order that denied certiorari. No separate writing is noted. Florida filed its response on Nov 2 without a docketed call for one. No amicus filed.

The baseline (`segment_base_rate`) and `brier_skill_score` belong to the harness: `stamp-cell` pools the interim substantive grant rate over prior application-Terms. I left both null and quote no rate of my own. The candidates report that the committed statpack carries no finer-reading counts for 2016-2025 (`finer_resolved` 0, `finer_unread` > 0). If that holds, the stamped rate should come back null because the pool falls below its registered floor and fails the zero-unread condition. I did not re-read the statpack to confirm this. `vote_accuracy` is omitted because this is not a merits cell. There are no `semantic_grades` (no declared semantic set on an interim cell). No band was frozen, so no flag is needed.

## Leakage
Forward mode. The prediction was made Nov 4, 2026, before the Nov 5 resolution. Nothing in the log or prose retrieves or presupposes this application's disposition. Graded `not_applicable`, `leakage_suspected: false`.

The logged calls are `outcome_only`, so I graded them on their queries. They are corpus lookups of 26-6013 and of recent applications, plus CourtListener reads of the Oct 29, 2026 Florida Supreme Court opinion below. That opinion predates the event and is legitimate forward signal.

## Score
P(grant) = 0.02 and the predicted label is `denied`, against `interim_granted` 0. So `correct` = 1 and Brier = 0.0004.

## Reasoning quality: 0.85
This is the strongest of the three rationales. It applies the Barefoot/Hollingsworth stay standard correctly. It also went beyond the five-page application and read the Florida Supreme Court opinion. That reading let it identify the three state-court holdings: the Woodard claim rejected on the merits because Guardado did get clemency review; the IAC/mitigation claims held untimely and procedurally barred, which is an adequate and independent state ground; and the 31-day warrant claim rejected. It anchored on a directly analogous Florida warrant stay denied two weeks earlier (26A524) and on the long string of Florida warrant cert denials. It correctly declined a scored anchor when the finer-reading pool failed. Small deductions: the descriptive substantive counts are recited at length to no real purpose, and some cited authorities are listed rather than analysed.

## Predicted reasoning: 0.8
I treated as central the disposition, its form (a short unsigned order paired with the cert denial), timing, the procedural path (referral, plus an opposition with no docketed call), and the absence of writings. Every one of these was borne out by the Nov 5 docket. The pairing with the cert denial and the response-without-request call are the most specific claims, and both held. The document stops short of 1.0 because its core calls (denial, referral, no writing) are what any competent reader of an execution-week Florida application would have forecast.
