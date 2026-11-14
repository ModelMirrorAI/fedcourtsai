# Evaluation: claude-baseline

## Outcome and mechanical scores

This is a **cert-stage** event. The November 13, 2026 docket entry grants the SG's reformulated misleading-omissions question, excluding the separate Item 303 issue. The committed outcome nevertheless uses the label `granted`, not `granted-in-part`, with `actual_granted: 1` and `disposition_route: plenary`.

- `correct = 0`: the prediction's literal `granted-in-part` label does not exactly match `actual_disposition: granted`. The evaluation contract requires exact-label comparison; I do not normalize or substitute labels.
- `brier_score = (0.84 - 1)^2 = 0.0256`: the probability forecasts any grant, and that event occurred.
- The categorical miss is a label mismatch, not a substantive miss on the limited scope of the grant. The prose accurately forecasts that scope. This distinction is flagged for maintainers without changing either score.
- No cert votes, merits judgment, or semantic claims are scored. Baseline and claim-score fields remain for harness computation; the relevant comparison is the stamped segment base rate, not an independently calculated replacement.

## Reasoning quality: 0.79

The rationale correctly prioritizes the invited SG/SEC recommendation, reformulation to ensure adversity, circuit disagreement, and a first genuine relist. It appropriately distinguishes three distributions from three post-consideration relists. It identifies the interlocutory posture and surviving Item 303 claim as reasons a grant is not certain. The staged SG brief supports the key limited-grant recommendation and directly addresses both adversity and the continuing required-statements claim.

Its main limitation is evidentiary depth: the candidate expressly did not closely read the BIO or the decision below and only skimmed respondents' supplement. That leaves the strongest adversity and vehicle objections less examined than the confidence of the 0.84 call might warrant. The asserted general-practice frequency of SG-supported grants is memory-based, not a measured conditional rate established by its retrieval. These are limitations in support, not evidence the forecast was irrational. I do not penalize the label mismatch again in this independent rationale grade, and I assert no discrepancy with a different statpack build.

## Predicted reasoning: 0.90

The central, discriminating call was a grant limited to Question 1 in the SG's reformulated wording. The staged November 13 order closely matches that forecast, including its additional-inquiry language and omission of Item 303. It also correctly calls plenary rather than summary review, no new CVSG, and no further distribution. The subsidiary expectation that announcement would follow on the next order list was off: the disposition is dated November 13 itself. That timing detail costs little relative to the correct scope and route.

The conditional merits account is unresolved, not confirmed by the question granted: there is no merits judgment or staged opinion. Conditional denial-writing predictions earn neither credit nor penalty because the Court granted review. The specific procedural forecast warrants a high grade independent of the quantitative label mismatch and of the less fully developed rationale.

## Leakage

The harness log records forward mode, 12 November 9 calls, and complete result-capture coverage. Queries concern the provisioned November 9 snapshot and filings, an October summary, statpack/schema material, and generic granted priors. No request seeks this petition's eventual disposition, and neither prose document presupposes the November 13 result. Captured digests are not a full reproduction of result bodies, but there is no affirmative own-case outcome evidence in the staged log or prose. `retrieved_outcome_material` is false, influence is `not_applicable`, and suspicion is false. The evaluator's later decided snapshot is not evidence of the predictor's information set.

## Scope and significance

No semantic-grades block is appropriate for this cert event or its null semantic-claims input. My independent significance assessment is 0.58: the case matters nationally to offering disclosures and securities litigation but presents a specialized statutory standard, not a major structural or constitutional question.
