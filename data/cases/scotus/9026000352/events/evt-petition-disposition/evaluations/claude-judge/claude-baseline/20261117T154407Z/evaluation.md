# Evaluation: claude-baseline, scotus/9026000352, evt-petition-disposition

**Outcome.** Cert-stage cell. The petition (No. 26-352, *Wray v. RTX Corporation*) was denied on November 16, 2026, after a single distribution for the November 13 conference; Justice Alito took no part. No CVSG, no relist, no noted dissent.

**Scores.** Predicted `denied` at P(grant) = 0.003: `correct` = 1, `brier_score` = 0.000009. The segment base rate, its basis and the skill score are the harness's to stamp and are left null here; claim scores are computed in code. No vote accuracy on a cert cell, and no semantic grades (no semantic set is declared at this stage).

## Reasoning (`reasoning_quality` = 0.76)

A concise, correct rationale. It anchors on the `baseline` reached rate and makes the useful observation that the band pools counseled petitions with real splits, so this petition sits at the bottom of that population. The adjustments are the right ones: self-represented petitioner, abstract questions that identify no statute or holding, an unpublished two-paragraph per curiam affirming a Rule 12 dismissal, no real split, and distribution with no response requested. The denial at the first conference bears it out. It is thinner than the other two: it does not engage the district court's actual grounds of dismissal or the petition's *Murray* argument, calls the questions "non-justiciable" where "not certworthy as framed" is what the record supports, and reads a terminal relist-0 bucket as context for a petition still pending without flagging the terminal-versus-hazard distinction. Its note for the conditional summary-route claim says a summary route is "somewhat more plausible than plenary review" while assigning it 0.3, a small internal inconsistency.

## Predicted reasoning (`predicted_reasoning_quality` = 0.68)

Central claims: denial, most likely on the order list after the November 13 conference; no further distribution and no call for a response; no CVSG; no GVR or summary reversal; no dissent or statement. All borne out on the staged docket and outcome. The QP-reformulation remark is conditional and the document itself says it will not happen. The forecast is terse and correct, and specific on timing, but commits to little beyond the expected trajectory of an obviously weak petition and offers the least supporting specificity of the three, so it sits a little under the 0.75 anchor. Justice Alito's recusal was not forecast, a marginal detail.

## Leakage

Forward cell, genuinely open when predicted. Log mode forward; prediction created 2026-10-31, before the 2026-11-13 conference and the 2026-11-16 denial. 15 fully captured calls: prompt and provisioned-record reads, a statpack grep and two corpus queries for unrelated denials; no web or MCP lookups. Nothing in the log or prose shows this petition's disposition; the reasoning treats the conference as still future. Graded `not_applicable`; `leakage_suspected` = false.

## Big case

My own read is 0.03: an individual, self-represented employment dispute resolved below on threshold pleading grounds, with no split, no amicus interest and no writing at denial.
