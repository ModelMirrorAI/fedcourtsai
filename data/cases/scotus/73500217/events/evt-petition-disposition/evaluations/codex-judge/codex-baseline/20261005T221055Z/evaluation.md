# Evaluation: codex-baseline

## Outcome and quantitative score

The cert-stage outcome is `denied`, `actual_granted = 0`, resolved October 5,
2026. codex-baseline predicted `denied` on September 17 with P(any grant) = 0.012.
Thus **correct = 1** and **Brier = (0.012 - 0)^2 = 0.000144**. This establishes
a correct disposition forecast, not judicial adoption of the candidate's analysis.

codex-baseline's own frozen context supplies Term 2025, band `baseline`, and
salience version `sal-v4`, matching the committed Markdown table. The baseline
is the bracketed reached-band rate pooled across every displayed prior Term,
OT2017–OT2024, using **risk_set**, not the terminal leading figure. Descending
Term rate/weighted-n pairs are 5.7%/1271, 5.9%/1312, 5.8%/1192, 5.6%/1500,
4.5%/1739, 4.6%/1399, 4.6%/1524, and 4.7%/1643. The rendered pool is
592.925 / 11,580 = **0.05120250431778929**. The table displays all ten of ten
Terms; the case's own OT2025 and later OT2026 are excluded. These are
denial-reweighted estimates from the committed table, not a current census.

The candidate reports an unrounded JSON-aggregate numerator of 593. I did not
substitute that reported number for the evaluator contract's rendered-table
calculation. The tiny precision difference is not a band, version, or window
mismatch. **Brier skill = 0.9450737326637661**, from
1 - 0.000144 / 0.05120250431778929^2. This describes one event only.

## Reasoning quality: 0.92

The rationale carefully separates what was supplied from inference: the
extension grant is not a cert grant; the response waiver explains the missing
opposition; and the absent appendix limits independent assessment of the
lower-court decision. It identifies the petition's strongest cert argument,
then explains why military-pay litigation against the government does not
necessarily conflict with rejection of a civilian implied remedy against a
hospital. That distinction is grounded in the supplied petition rather than
merely asserting that a controversial case is routine.

Its treatment of section 337(a) and the private-right/private-remedy distinction
is specific and measured. It describes Buckman as an obstacle rather than a
holding resolving this EUA question. The staged log records targeted precedent
lookups consistent with the rationale's account; I have not independently
retrieved those opinions. The candidate appropriately avoids treating the
petition's medical characterizations as adopted facts or inventing preservation
defects. It uses the correct reached-band prior-Term population and explicitly
distinguishes terminal relist rates from forward transition probabilities.

The remaining limitation is the size of the probability adjustment. Moving
from approximately 5.12% to 1.2% is reasoned judgment, not a fitted estimate
supported by a matched sample. The lower-court account still comes principally
from the petition, and the asserted conflict was not exhaustively researched.
Those limits keep the score below 1.0; the eventual denial does not independently
validate every doctrinal premise or prove calibration.

## Leakage and scoring boundaries

The harness records forward mode and 32 calls on September 17, before the
October 5 denial. Thirty results are captured; two web calls are unobserved,
for coverage 0.9375. Although the candidate says those calls returned no usable
content, the harness does not establish that: unobserved is not empty. Their
visible queries target a general statutory page, not this petition's outcome.
The other visible research concerns existing authorities. Nothing in the log
or prose indicates retrieval of the eventual disposition or an already-decided
case routed forward. I record no retrieved outcome material, `not_applicable`
influence, and no suspected leakage.

The forecast document was read only for context. Neither it nor the quantitative
claims or stakes score enters reasoning quality. Claim scoring remains with the
harness; cert votes and semantic propositions are not scored here. The optional
independent stakes assessment is omitted because candidate stakes material has
already been seen. No external retrieval was needed.
