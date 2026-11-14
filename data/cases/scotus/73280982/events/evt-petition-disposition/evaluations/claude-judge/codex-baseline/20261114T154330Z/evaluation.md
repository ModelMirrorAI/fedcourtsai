# Evaluation — codex-baseline

**Cell:** scotus/73280982, `evt-petition-disposition`, cert stage, forward mode. Outcome: `granted` (plenary), resolved 2026-11-13; the order grants review limited to one question, in the Solicitor General's reformulated wording, after one post-CVSG relist.

## Scores

- `correct` = 0: predicted `granted-in-part`, outcome label `granted`. This is the exact-label rule applied as written. The order itself reads "Petition GRANTED limited to the following question", so the candidate's label describes what the Court did more closely than the outcome's label does; the 0 reflects the outcome vocabulary, not a wrong call. I flagged it in `flags.json`.
- `brier_score` = (0.82 − 1)² = 0.0324.
- Base rate, skill and claim scores are the harness's; I wrote none. No votes are scored on a cert cell.

## Reasoning quality — 0.85

The most careful of the three on method. It pools the `high` band's risk-set rate over Terms strictly before 2025 (314/898 = 34.97%), which matches the statpack build it ran against (`eb6830084a18`, rebuilt with `statpack-at`), and explains why the whole-population, circuit and terminal relist-bucket rates are the wrong anchors for a post-CVSG petition. It says outright that no table conditions on a favourable SG recommendation and that the move to 0.82 is judgment, not a measured frequency.

The case analysis is grounded in the filings: the SG's reformulation as the answer to the parties' apparent agreement on the original wording, the opposition's convergence and pleading-stage arguments as the reason not to go near certainty, and the weakness of Question 2 as the source of most of the residual risk. That last point led directly to the limited-grant call. It is candid about limits: the mis-extracted questions file, the truncated petition, the unread supplemental briefs, and web searches that returned nothing.

It is less detailed than gemini-baseline on the doctrine and does not address the recent securities DIGs by name, but nothing in it is unsupported, and its probability was the best calibrated of the three.

## Predicted reasoning — 0.95

Central claims: a grant limited to the first question as reformulated by the United States, with the Item 303 question outside it; one further distribution before the grant, in November or December; plenary review; and a conditional merits ground.

The document commits flatly to the limited, reformulated grant, and the order matches it. It also reads the two-distribution state correctly as a post-CVSG return rather than two relists, and calls one more distribution before the grant; the docket shows exactly that. Both were calls a competent reader could have made otherwise. Plenary review was the expected route. The merits ground and the denial branch are conditional and earn nothing either way. The 0.60 on the relist is a moderate commitment rather than a strong one, which is the only reason this is not at the very top.

## Leakage

Forward cell, run 2026-10-26, before the 2026-11-13 resolution. The log shows provisioned-file and statpack reads and three web-search rows whose results are unobserved; graded on their queries, they target the 2024 *Macquarie* opinion, a general precedent, not this petition. The candidate's `retrieval.md` discloses them. `not_applicable`.

## Big case

My read is 0.55: a nationally significant Section 11 question for IPO disclosure and securities litigation, backed by the SG and SEC, but technical statutory doctrine.
