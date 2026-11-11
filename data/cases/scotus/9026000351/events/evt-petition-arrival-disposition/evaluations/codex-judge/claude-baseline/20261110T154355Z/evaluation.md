# Evaluation: claude-baseline

## Outcome and mechanical scores

This is a cert-arrival cell. The predicted disposition, denied, exactly matches the November 9, 2026 outcome: correct = 1. With P(any grant) = 0.005, the Brier score is (0.005 - 0)^2 = 0.000025. Cert votes are not scored. No merits judgment comparison or semantic-grades block applies. The structured quantitative claims are reserved to the harness, not evaluated here or folded into reasoning_quality.

Baseline, skill and baseline basis remain null for harness stamping. I assessed the rationale's base-rate use against the candidate-time build returned by `fedcourts statpack-at`, not today's checked-out pack: `2420d5dd72e1dd97585b5f0c998b82f40c3b5a32`, digest `sha256:e9eca3b07e3f204061568dcba95bff0999a83b04ae841ed82d5898136aed485c`, landed September 26. The sal-v4 baseline reached risk set across displayed prior Terms 2017-2025 is 638 / 12,720 = 5.0157%, with a denial-reweighted denominator. The rationale's rounded 5% reference is appropriate for a private petitioner at arrival, and it correctly avoids the terminal baseline and federal-petitioner column.

## Reasoning quality

Score: **0.77**. The rationale correctly identifies a strong combination of vehicle problems: the constitutional issue was not reached below, the petition seeks departure from the monetary-claims jurisdictional rule, the appellate decision is a summary affirmance, and no developed conflict is demonstrated. The petition's page-7 footnote and the currently staged appendix, App-2 to App-3, support the jurisdictional and preservation analysis. The appendix was fetched after prediction, so I do not assume it was available then. The candidate transparently discloses its partial reading of the petition and rejects noncomparable interim priors rather than using them as cert comparators.

The analysis is less careful about the strength of several conclusions: it presents a sub-1% frequency for this kind of pro se petition without identifying a measured subgroup; says the GVR route is closed rather than merely unsupported by an identified intervening decision; and converts the expectation of no CVSG into an unsubstantiated categorical assertion that one cannot issue. The staged materials establish the outcome here, not those universal propositions. These weaknesses matter to the rationale's soundness independently of its successful headline prediction. A low point estimate is plausible, but its precision is not empirically established. Denial does not prove the Court adopted any particular jurisdictional rationale.

## Predicted reasoning

Score: **0.90**. The forecast correctly commits to first-conference denial, a government waiver without a response request, exactly one distribution, no CVSG and no noted separate denial writing. The staged chronology confirms those predictions. One secondary timing claim fails: the document explicitly puts the Clerk's distribution in early-to-mid November, whereas the distribution occurred October 21 for the November 6 conference. A November conference is not a November distribution. This modest timing miss does not outweigh the accurate disposition and procedural route.

The conditional choice of QP 3 and the alternative summary route are untested because certiorari was denied; they earn neither credit nor penalty. The forecast of the companion petition's long-conference treatment is unresolved in this cell: the staged docket does not record that other petition's disposition. It is not silently scored as either a hit or a miss. The five claims driving the grade, including the timing miss, are recorded in evaluation.json.

## Leakage assessment

The harness log marks forward mode and captures results for all 27 calls. The calls occurred September 27, before this target was denied November 9. Its corpus lookup, RECAP history searches, and target/companion docket searches do not show retrieval of the target's resolved outcome. The recorded RECAP date, December 17, 2025, predates the baseline. Related proceedings already described in the petition are not the target outcome. There is no evidence of mis-provisioning an already-decided target: influenced_prediction is not_applicable and leakage_suspected is false. The candidate's searches are not evaluator retrievals.

## Significance and limits

My independent stakes assessment is **0.25**, based on the potential governance questions but the indirect jurisdictional vehicle and absence of any merits precedent from the denial. No required input is missing or malformed, and no blocker requires flags.json.
