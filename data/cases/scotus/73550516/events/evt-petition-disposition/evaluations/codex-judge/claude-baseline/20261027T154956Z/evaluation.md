# Evaluation: claude-baseline

## Outcome and quantitative assessment

This is a cert-stage event. The supplied outcome records **dismissed** on October 20, 2026, with `actual_granted = 0`. The October 26 snapshot records an October 19 joint stipulation followed by an October 20 Rule 46 dismissal. It does not record a denial or a resolution of the arbitration question.

The prediction named **denied**, so exact-label `correct = 0`. Its 0.20 grant-family probability produces `(0.20 - 0)^2 = 0.04`. The non-grant binary was favored, but that does not make denial the correct disposition. No cert votes are scored.

The prediction froze `baseline` under `sal-v4`, Term 2025. The **stamped segment base rate**, its basis, and Brier skill are the harness's; no independent anchor or skill estimate is supplied here. Mechanical claims and the forecast document are not graded, and no semantic set applies to this cert cell.

## Reasoning quality: 0.80

The rationale identifies the reserved governing-law question, distinguishes an independent plenary grant from a follower GVR, and connects the petition's hold request to the unpublished decision's express reliance on Town of Vinton. It gives an explicit conditional probability decomposition and recognizes missing opposition, vehicle objections, and imperfect docket coverage. Those are substantial analytical strengths independent of the eventual disposition.

The main weaknesses are the judgmental lead-case grant estimate and the unsupported certainty that the response request removed the petition from its scheduled conference. The supplied record does not independently establish that procedural consequence. The rationale does acknowledge withdrawal or dismissal as residual possibilities, so the realized Rule 46 exit was not conceptually excluded. Its occurrence nevertheless illustrates why procedural continuation should not be treated as nearly mechanical. Dismissal provides no evidence that either side's choice-of-law position was right or wrong; the quality grade concerns the rationale, not whether its forecast prose or mechanical claims came true.

## Leakage

The log is **forward**, with 48 calls and result-capture coverage 1.0. Research occurred October 5-6, before the October 19 stipulation and October 20 dismissal. The log includes this petition's docket checks and companion-case research, but the staged reasoning and retrieval note report no disposing material. Nothing in the available dates or prose contradicts that account. Current docket research was allowed for an unresolved forward cell. `retrieved_outcome_material = false`, influence is `not_applicable`, and `leakage_suspected = false`.

Only provisioned evidence was used for this evaluation; no external case facts were retrieved.
