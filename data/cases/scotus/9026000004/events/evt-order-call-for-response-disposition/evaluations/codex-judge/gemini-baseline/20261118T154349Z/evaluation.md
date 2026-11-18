# Evaluation: gemini-baseline

This cert-stage prediction correctly called denial. The recorded outcome is a standard denial on November 16, 2026, with `actual_granted: 0` and no noted dissent. Its grant probability was 0.08, so `correct = 1` and `brier_score = (0.08 - 0)^2 = 0.0064`. Votes are not scored at the cert stage. The segment baseline and skill belong to the harness; quantitative claims are left for its mechanical scorer, and this stage has no semantic grades.

## Analytical reasoning

`reasoning_quality = 0.20`. The rationale identifies the real general issue: whether Georgia's judicial construction of business registration supplies adequate notice of consent to general jurisdiction after *Mallory*. Treating a response request as attention rather than assurance of a grant is also sensible. But the main vehicle analysis rests on a materially different case history, with precise quotations and appendix references that the staged record does not support.

The petition's statement (pp. 8-14) and actual appellate opinion (App. 2a-13a) concern a Georgia resident injured in Georgia and litigation in Chatham County over a $10,860,972 default judgment. They do not describe a Texas plaintiff injured in Texas, a Fulton County discovery dispute, or the alleged July and October 2025 orders. The Georgia Court of Appeals issued a reasoned opinion on June 23, 2025; the Georgia Supreme Court denied review March 31, 2026. Both differ from the rationale's asserted unreasoned appellate denials and dates. The petition identifies registration in 1985, not 1989; the staged docket identifies Greenberg Traurig counsel, not Mayer Brown. These errors directly undermine the analysis of finality, waiver, and an independent state ground. Genuine preservation and default problems exist, but they do not authenticate the invented procedural account.

Statistical use was checked against historical statpack build `7bcde3b105cb212283905eda17b827efc188e80c` (`sal-v4`), recovered with `statpack-at`, rather than today's `sal-v8` pack. The rationale's purported pooled risk-set counts and recent-Term figures do not match that build. The pack also supplies no table establishing the claimed response-request-conditioned historical ranges. This is a substantiation defect, not a penalty for disagreeing with a later refresh. No independently pooled scoring baseline is supplied here; the stamped segment base rate remains authoritative.

## Predicted reasoning

`predicted_reasoning_quality = 0.50`. The central procedural trajectory was specific and borne out: response and reply, a second distribution, no CVSG, and a plain denial without noted dissent. The docket shows the opposition filed October 14, reply and redistribution October 28, conference November 13, and denial November 16.

The document also gives substantial weight to the opposition exposing the specified discovery-stage orders and expired-term history. That account is not borne out: the actual opposition addresses preservation, litigation concessions, and default admissions in this default-judgment dispute (BIO pp. 14-24). Its broad expectation of vehicle objections has some support, but its central concrete explanation is wrong. The Court's own reasons remain unresolved because the denial is unexplained; the opposition is advocacy, not the Court's holding. Conditional grant scope and route were never reached and carry no credit or penalty. The correct, specific trajectory and failed central factual account place this forecast at the mixed-specific-forecast anchor.

## Leakage and significance

The log identifies a forward prediction made October 29, before resolution. Its calls have `outcome_only` capture and 0.0 captured-result coverage; null dates are not evidence that searches returned nothing. Query scopes and prose show no later disposition of this petition. The own-caption MCP query was logged as throttled. `influenced_prediction` is `not_applicable`, with `leakage_suspected: false`; the rationale's factual errors do not establish leakage.

My independent significance assessment is 0.50: corporate consent to general jurisdiction has substantial commercial and interstate importance, while this individual damages dispute's default posture limits its reach as a vehicle. The denial establishes no rule on the constitutional question.
