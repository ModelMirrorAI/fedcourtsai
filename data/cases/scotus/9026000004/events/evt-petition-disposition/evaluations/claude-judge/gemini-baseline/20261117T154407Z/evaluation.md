# Evaluation: gemini-baseline — scotus/9026000004, evt-petition-disposition

**Outcome:** petition denied on November 16, 2026, with no noted dissent, no CVSG, and no distribution beyond the two already on the docket.

**Scores:** `correct` 1 (predicted `denied`), Brier 0.0009 (p = 0.03 against 0), the best number of the three. This is a cert cell; the segment base rate, basis and skill are the harness's to stamp.

## Reasoning (`reasoning_quality` 0.35)

The number was good, but the rationale rests in part on docket facts that the staged record contradicts. Every docket entry below predates the prediction, so the snapshot it read on October 29 carried them.

| What the rationale states | What the docket and petition appendix show |
| --- | --- |
| Brief in opposition filed September 2; reply filed September 16 | September 2 was the extension motion; the brief in opposition was filed October 14 and the reply October 28 |
| Distributed September 29 for an October 16 conference, rescheduled October 15, redistributed October 19 for October 30 | Distributed July 22 for 9/28 and October 28 for 11/13; no reschedule entry exists |
| Georgia Supreme Court denied certiorari 5–4 on March 3, 2026, with four justices voting to grant | The order is dated March 31, 2026 and says all participating Justices concurred (two disqualified, one not participating) |
| Samsung first registered in Georgia in 1982 | The petition says 1985 |

The first of its four downward adjustments ("a pre-conference reschedule, not a post-conference relist") is built on the invented reschedule. Its conclusion happens to be near the truth, because the second distribution really was not a post-conference relist, but the real reason is the call for a response, which the rationale never mentions. The 5–4 state-court vote is then used as a reason to keep the probability off the floor.

What is sound: the anchor arithmetic is correct and well laid out, and the follow-on denials it cites (Cooper Tire, Syngenta v. Nemeth, Norfolk Southern v. Mallory II) are real. I confirmed the latter two in the corpus and in the brief in opposition. The forum-nexus and default-judgment vehicle points are also fair readings of the brief in opposition. It does not engage the preservation objection, which is the brief in opposition's lead argument.

A rationale that reaches a well-calibrated number while misstating the procedural history it reasons from cannot grade as sound analysis.

## Predicted reasoning (`predicted_reasoning_quality` 0.5)

Central claims: denial, the route (first consideration at an October 30 conference after a reschedule, then denial with no further distribution), no CVSG, and no separate writing. Denial, no CVSG and the silent order were borne out.

The route claim was specific and its stated path did not exist: there was no October 30 conference and no reschedule. The underlying count forecast (no further distribution) did hold. That makes it a specific forecast split between borne out and not, which is the 0.5 anchor. The conditional if-granted content earns neither credit nor penalty.

## Leakage

Forward cell; `not_applicable`. The log's results are `outcome_only` throughout, so I graded calls on their queries. They are the provisioned record, the statpack, corpus lookups of petitions resolved before the prediction, and two throttled CourtListener searches. One search used this case's caption, but it ran eighteen days before any disposition existed. Nothing in the reasoning presupposes the outcome.

## Big case

My own read is 0.35: a nationally relevant jurisdiction question in a poor, fact-bound vehicle, denied silently.
