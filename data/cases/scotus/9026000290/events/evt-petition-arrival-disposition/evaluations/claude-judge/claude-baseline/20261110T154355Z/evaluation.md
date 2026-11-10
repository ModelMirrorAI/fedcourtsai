# Evaluation — claude-baseline, evt-petition-arrival-disposition (scotus/9026000290)

**Stage:** cert (arrival moment, forward). **Outcome:** `denied` on 2026-11-09 after one distribution (conference of 11/6/2026). There was no CVSG and no noted dissent.

## Score

- Predicted `denied` with P(grant) = 0.004. `correct` = 1; Brier = 0.004² = 0.000016.
- The segment base rate, its basis and the skill score are left to the harness stamp. Compare against "the stamped segment base rate".
- No votes were predicted, and votes are never scored on a cert cell.

## Reasoning (`reasoning_quality` = 0.85)

This is the strongest rationale of the three. The anchor is the sal-v4 `baseline` reached rate pooled over OT2017–OT2025 (≈5.0% over about 12,700 weighted petitions). That matches the build it ran against, which I rebuilt with `statpack-at` (2420d5dd72e1). It explicitly declines the terminal relist-0 figure.

The adjustments are ordered sensibly:
1. **Pro se filer.** This is correctly identified as the largest discount.
2. **No split.** It makes the sharp point that the QPs posit a conflict among the Court's own cases, and that those lines are reconcilable under the public-vantage rule.
3. **Vehicle.** It cites the summary writ denial, the demurrer to a seventh amended complaint, a state court as named respondent, and statutory provisions unrelated to the QPs.
4. **Stakes.**

It also reconciles the snapshot's lower-court field against the petition's jurisdictional statement. One weakness is that the pro se discount is asserted without a figure. Another is that it frames the class floor as "the scored yardstick", which edges toward forecasting the scorer rather than the case. Neither changes the soundness of the conclusion.

## Leakage

The cell is forward. The prediction was made 2026-09-27. The log has 15 calls, all captured. They are reads of the provisioned inputs and the statpack, plus generic `fedcourts query` calls that pulled 2020s SCOTUS rows not filtered to this docket. Those calls are disclosed in retrieval.md as uninformative. There were no web or MCP calls, no post-resolution material and no reads of `data/qp-topics/`. The grade is `not_applicable`.

## Big case

My own read is 0.03.

## Predicted reasoning (`predicted_reasoning_quality` = 0.80)

The central claims were:
1. Denial on the papers with no separate writing — **borne out**.
2. Exactly one distribution, for a late-October or early-November conference, with denial by mid-November — **borne out**. The petition was distributed Oct 21 for the 11/6 conference and denied 11/9. This was the most specific timing call of the three and it landed.
3. The City waives its right to respond — **unresolved**. No BIO and no waiver entry appear on the docket. Distribution after the Oct 5 deadline fits no response having been filed, but a waiver itself is not shown.
4. No CVSG — **borne out**.

The document is specific and correct on everything the record settles. It sits below 1.0 because the path it called was still the modal one for such a petition, and one secondary claim cannot be confirmed from the record. The conditional merits forecast ("if granted … affirm") earns neither credit nor penalty.
