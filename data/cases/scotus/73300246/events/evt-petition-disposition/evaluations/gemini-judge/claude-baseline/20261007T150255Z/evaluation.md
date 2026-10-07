# Evaluation of claude-baseline

claude-baseline predicted a denial with a P(grant) of 0.015, which was correct.

The reasoning was excellent (quality 0.9). It correctly identified the `risk_set` segment base rate of 5.12% for the `sal-v4` baseline band using the correct OT2017 to OT2024 terms from the statpack. The predictor then applied a discount due to the case being an unpublished order from a state court, noting the presence of adequate and independent state grounds, and significant fact-bound issues.

There is no sign of leakage. The mode is forward and the retrieval log shows no access to outcome-revealing information.
