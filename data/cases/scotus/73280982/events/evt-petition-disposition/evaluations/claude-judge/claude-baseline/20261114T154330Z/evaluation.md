# Evaluation — claude-baseline

**Cell:** scotus/73280982, `evt-petition-disposition`, cert stage, forward mode. Outcome: `granted` (plenary), resolved 2026-11-13; the order grants review limited to one question, in the Solicitor General's reformulated wording, after one post-CVSG relist.

## Scores

- `correct` = 0: predicted `granted-in-part`, outcome label `granted`. This is the exact-label rule applied as written. The order itself reads "Petition GRANTED limited to the following question", so the candidate's label describes what the Court did more closely than the outcome's label does; the 0 reflects the outcome vocabulary, not a wrong call. I flagged it in `flags.json`.
- `brier_score` = (0.72 − 1)² = 0.0784.
- Base rate, skill and claim scores are the harness's; I wrote none. No votes are scored on a cert cell.

## Reasoning quality — 0.75

A short, disciplined rationale. The anchor is right: it pools the `high` band's risk-set rate over Terms strictly before 2025 (314/898, about 35%), which matches the statpack build it ran against (`eb6830084a18`, rebuilt with `statpack-at`), and cross-checks it against the CVSG cut. It then moves on the one signal those cuts do not condition on, the SG's recommendation to grant Question 1, and says plainly that its 70–80% follow rate is a remembered figure and not a pack rate. The discounts are sensible: interlocutory posture, a disputed split, the reformulation, and recent securities DIGs. It also caught the mis-cut `questions-presented.txt` and worked from the SG's restatement.

It sits below the others on depth. The legal analysis is a list of factors rather than an engagement with the filings' arguments, and it does not explain why the vehicle objections were weaker here than in the DIG'd cases. Its 0.72 was the most cautious of the three on a petition the Court granted. The relist reasoning ("the Court rarely grants without a relist") was correct and correctly applied.

## Predicted reasoning — 0.90

Central claims: a grant limited to Question 1 in the SG's wording with Question 2 left behind; at least one further distribution and a grant in mid/late November or early December; plenary review; and a conditional merits ground.

All three resolvable claims are borne out, and two were discriminating. The scope call matches the order's text, where a grant of both questions or of the petition's own wording was open. The procedural path matches the docket closely: redistributed November 9 for the November 13 conference, granted November 13. Plenary review was the expected route. The document hedges its scope call slightly ("most likely", "or a close variant"), which keeps it just under the top anchor. The merits ground and the denial branch are conditional and earn nothing either way.

## Leakage

Forward cell, run 2026-10-26, before the 2026-11-13 resolution. The log is fully captured and shows only reads of the provisioned snapshot, briefs, schemas and the committed statpack. `not_applicable`.

## Big case

My read is 0.55: a nationally significant Section 11 question for IPO disclosure and securities litigation, backed by the SG and SEC, but technical statutory doctrine.
