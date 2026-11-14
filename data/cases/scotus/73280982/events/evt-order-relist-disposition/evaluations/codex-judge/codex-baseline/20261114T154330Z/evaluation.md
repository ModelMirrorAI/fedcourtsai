# Evaluation: codex-baseline

## Outcome and mechanical scores

This is a **cert-stage** event. On November 13, 2026, the Court granted a reformulated question asking whether materiality can establish a Section 11(a) misleading omission without an additional inquiry into whether an affirmative statement was misleading. The separate Item 303 question is outside the grant. `outcome.json` labels this `granted`, with `actual_granted: 1` and `disposition_route: plenary`.

- `correct = 0`: `granted-in-part` is not an exact match to `granted`. The explicit comparison contract controls; the accurate limited-grant prose does not authorize relabeling the prediction or the outcome.
- `brier_score = (0.79 - 1)^2 = 0.0441`.
- The label asymmetry is flagged because the scope forecast was substantively correct despite the mechanical miss. Neither score is adjusted.
- Cert votes are not scored. There is no merits judgment or applicable semantic-grades block. Baseline and claim scores are reserved for the harness; any baseline comparison uses the stamped segment base rate.

## Reasoning quality: 0.93

This is a well-supported rationale rather than simply a successful grant call. It distinguishes the frozen risk-set anchor from terminal marginal tables, avoids multiplying correlated signals, and explicitly says no provided table estimates the SG-recommendation-plus-relist conditional probability. It correctly separates three distributions from one genuine post-SG relist and explains the effect of the prior CVSG.

The legal analysis distinguishes misleading omissions from required statements, reads the SG recommendation in its reformulated form, and engages respondents' adversity and surviving-Item-303 arguments. The staged SG brief supports those points: printed p. 18 rejects interlocutory posture as a sufficient obstacle, printed p. 19 proposes reformulation to ensure adversity, and printed pp. 23–24 explain why the surviving claim does not defeat review of Question 1. The rationale correctly avoids treating Macquarie's Rule 10b-5 holding as eliminating Section 11's independent required-disclosure liability. It is transparent about selected reading, truncated lower-court materials, and the judgmental probability adjustment.

The precise weight assigned to recommendation and relist remains unestimated, and the independently described historical retrieval is not a measured cohort establishing 0.79. Those limitations keep the grade below perfect but do not undermine the basic analysis. The literal disposition-label mismatch is not a reason to lower this separate rationale assessment. No claim is made that its quoted historical tables disagree with a later committed statpack build.

## Predicted reasoning: 0.95

The central forecast is specific: a limited grant in the SG's formulation, excluding Item 303, on a plenary route without another distribution. The actual November 13 entry closely matches its predicted question wording; the outcome confirms the route and unchanged distribution count. No additional CVSG appears. These are meaningful procedural alternatives, not merely restatements of the petition's subject.

The conditional discussion of a later ruling's consequences remains unresolved because this event records only certiorari. The grant does not establish the Court's substantive answer or eventual litigation effects. The alternative denial-writing path never arose and adds neither credit nor penalty. No unstaged opinion or order has been fetched to fill those gaps. The grade concerns this document alone, not the rationale's detail, headline probability, or structured claim probabilities.

## Leakage

The harness log records forward mode and 32 November 9 calls before the November 13 grant. Thirty results are captured; two historical-precedent web calls are unobserved. Those unobserved calls are assessed from their queries, not treated as having returned nothing. Their targets are historical Macquarie/Omnicare authorities and a 2024 slip-opinion URL, not Robinhood's later disposition. Captured CourtListener calls concern the historical Macquarie opinion, dated April 12, 2024. The visible local reads concern the provisioned November 9 record, and no own-case deciding order or post-resolution fact appears in the prose. `retrieved_outcome_material` is false, influence is `not_applicable`, and suspicion is false. This assessment does not assume the predictor saw the evaluator's later snapshot.

## Scope and significance

This cert event has no declared merits semantic set, and the prediction has no semantic-claims block; no semantic grading is written. My independent significance assessment is 0.58, based on recurring national IPO-disclosure consequences within a bounded statutory issue.
