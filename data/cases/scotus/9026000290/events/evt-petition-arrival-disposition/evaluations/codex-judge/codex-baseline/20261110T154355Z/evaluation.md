# Evaluation: codex-baseline

## Outcome and mechanical scores

This is a cert-stage arrival cell. The petition was denied on November 9, 2026. The staged docket records a single October 21 distribution for the November 6 conference, followed by denial. The outcome records no CVSG and no noted dissent from denial.

The predicted disposition, denied, matches exactly: correct = 1. With P(grant) = 0.004 and actual_granted = 0, Brier = (0.004 - 0)^2 = 0.000016. Cert votes are not scored; judgment accuracy and semantic grading do not apply. The structured claims are left entirely to the harness. Baseline and skill fields are also left to the harness; the comparison is against the stamped segment base rate, not an independently supplied rate.

## Reasoning quality: 0.92

This grade concerns reasoning.md alone. The analysis distinguishes the petitioner's asserted conflict among Supreme Court precedents from a demonstrated appellate split, identifies the unexplained state writ disposition, and treats finality, preservation, and alternative grounds as uncertainties rather than established jurisdictional defects. That caution fits the staged petition: App. 2 supplies no substantive constitutional holding, and App. 3 ends with a notice that additional material is available in the Clerk's Office. The discussion appropriately treats the petitioner's factual and constitutional characterizations as advocacy and does not infer a respondent concession from an absent brief.

The probability adjustment remains judgmental rather than empirically fitted, but its case-specific direction is well supported by the limited vehicle and absence of a demonstrated conflict. The denial does not establish that the Court adopted any of these reasons. This is not a reward merely for predicting the winning label, and no impression of the structured claims or forecast document enters this grade.

For historical base-rate use I recovered statpack build 2420d5dd72e1dd97585b5f0c998b82f40c3b5a32, digest sha256:e9eca3b07e3f204061568dcba95bff0999a83b04ae841ed82d5898136aed485c, using statpack-at. This is the candidate-time build, not a substitution of today's checked-out pack. Its sal-v4 risk-set table supports the candidate's choice of the private baseline reached population and strictly prior Terms. I do not restate a separately pooled rate. The candidate's cited publication commit is not treated as an underlying-corpus freshness stamp.

## Predicted reasoning: 0.90

The central forecast was denial through one conference distribution, without another relist or CVSG, during November or December after the response deadline. Those are specific procedural commitments, not just a generic low-cert-probability statement, and all are borne out by the staged docket and outcome. The forecast correctly distinguishes the initial distribution from a later relist.

No noted dissent is recorded. However, the staged materials do not include the disposing order's text, so the stronger assertion of an unsigned order without any separate statement remains unresolved rather than a miss. The conditional question selection and plenary-versus-summary discussion earn neither credit nor penalty because the petition was not granted. No constitutional ground can be inferred from the bare denial.

## Leakage and significance

The retrieval log is forward and the prediction predates resolution. Its 34 calls include 29 captured results and five unobserved general-authority web calls. The latter cannot substantiate an empty-result claim, but their queries do not seek this petition or its disposition. Local reads concern the provisioned snapshot, petition, schemas, and statpack. No evidence shows this case's own eventual disposition surfacing before the forecast. Leakage influence is not_applicable; leakage_suspected is false.

My independent significance assessment is 0.10: the Fourth Amendment topic has potential general reach, but the demonstrated case is a localized dispute without a developed appellate conflict or identifiable institutional stakes. No blocker prevents evaluation.
