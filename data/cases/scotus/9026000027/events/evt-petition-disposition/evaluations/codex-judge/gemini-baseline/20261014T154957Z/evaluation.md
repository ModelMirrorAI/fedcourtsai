# Evaluation: gemini-baseline

## Outcome and scores

This is a cert-stage distribution cell. The supplied outcome records denial on October 13, 2026, with `actual_granted = 0`. gemini-baseline's October 4 prediction names `denied`, so `correct = 1`. Its grant-family probability is 0.005; `(0.005 - 0)^2 = 0.000025` is the Brier score. This low realized loss is not independent evidence that the estimate was well calibrated.

The prediction froze the baseline band under sal-v4 for Term 2026. The stamped segment base rate and skill belong to the harness; I leave their fields absent rather than pooling a competing anchor. Cert votes are unscored, no semantic grading applies, and claim scores are harness-owned. The separate forecast document was read only for context and contributes no grade.

## Reasoning quality: 0.62

The short rationale is directionally supported by the supplied briefs: it identifies a narrow Louisiana statutory-employer dispute, recognizes the proposed federal-inspector issue, and observes the absence of a demonstrated circuit split. It treats the opposition's characterization as an attributed argument rather than claiming an independently retrieved holding. Those are relevant reasons to prefer denial, and the realized denial is consistent with that forecast.

However, the rationale omits the record's strongest concrete vehicle problem: the opposition's account that the FECA-conflict theory was first raised on reconsideration and the Supremacy Clause argument first on appeal. It also does not explain the distinction between the two-contract defense and the trade-or-business inquiry that occupies much of the petition. Its downward adjustment relies heavily on pro se status and the absence of experienced Supreme Court counsel, without a demonstrated empirical mapping from those features to 0.005. The prior is described loosely, without a rendered-Term window or a reproducible weighting explanation. Brevity itself is not penalized; the substantive omissions and weakly justified magnitude of the adjustment are the reason this is a moderate rather than high reasoning score.

The denial does not establish that the Court adopted the opposition's view or rejected the underlying federal argument on its merits. The reasoning grade is independent of the favorable Brier loss.

## Leakage assessment

The harness log records forward mode and October 4 calls, all preceding the October 13 resolution. Its result-capture coverage is 0.0: every result is unobserved, so null dates and absent digests cannot establish that the searches returned nothing. In particular, the retrieval note's claimed CourtListener rate limit is not independently verified by this log. The queries show reads of the October 4 snapshot and briefs, a caption search, and an opinions-endpoint request using the lower-court docket number; none expressly seeks a later Supreme Court disposition. The reasoning contains no already-decided language or outcome-revealing facts. Thus no affirmative outcome exposure appears, and there is no evidence of a decided case provisioned forward: `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`. This is a timing- and query-based assessment, not a claim of complete result visibility.
