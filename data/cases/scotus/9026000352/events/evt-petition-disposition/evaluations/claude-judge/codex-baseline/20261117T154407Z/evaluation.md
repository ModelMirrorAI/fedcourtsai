# Evaluation: codex-baseline, scotus/9026000352, evt-petition-disposition

**Outcome.** Cert-stage cell. The petition (No. 26-352, *Wray v. RTX Corporation*) was denied on November 16, 2026, after a single distribution for the November 13 conference; Justice Alito took no part. No CVSG, no relist, no noted dissent.

**Scores.** Predicted `denied` at P(grant) = 0.003: `correct` = 1, `brier_score` = 0.000009. The segment base rate, its basis and the skill score are the harness's to stamp and are left null here; claim scores are computed in code. No vote accuracy on a cert cell, and no semantic grades (no semantic set is declared at this stage).

## Reasoning (`reasoning_quality` = 0.86)

The rationale is the most careful of the three. It starts from the frozen `baseline` reached anchor and explicitly distinguishes it from terminal-bucket figures, declining to read the statpack's relist/CVSG/amicus cuts as transition hazards or to multiply marginal cuts together. The downward adjustment rests on the right vehicle facts from the appendix: an unpublished Fourth Circuit per curiam, questions presented that do not isolate the grounds of dismissal (no private right of action, pro se qui tam bar, SOX administrative prerequisites, Dodd-Frank pleading), and a claimed conflict with *Murray* that does not match the ground actually decided (causation/intent versus exhaustion), with the district court itself citing *Murray* so no GVR hook exists. It is appropriately restrained about what the record does not show (no inference from the absent brief in opposition, no adoption of the petition's national-security allegations) and candid about failed lookups. The Court denied at the first conference, as the analysis implied. Small deductions: it did not weigh the petitioner's self-represented status or the no-response posture as explicitly as it might have, and the write-up spends considerable space on process caveats relative to substance.

## Predicted reasoning (`predicted_reasoning_quality` = 0.7)

Central claims: denial on the order list after the November 13 conference without opinion; zero further distributions; no CVSG; no dissent or statement. All four are borne out by the staged docket and outcome. The conditional QP-narrowing and plenary-versus-summary content hangs on a grant that never happened and is neither credited nor penalised. The document is specific about timing and route, but for this petition every one of those calls was the overwhelmingly expected one, so there is little a competent reader could have called otherwise; that keeps it below the top anchor. Justice Alito's recusal was not forecast, a marginal detail that costs nothing material.

## Leakage

Forward cell, genuinely open when predicted. Log mode forward; prediction created 2026-10-31, before the 2026-11-13 conference and the 2026-11-16 denial. Calls are provisioned-record reads, statpack reads, two corpus queries for unrelated denials, two web searches (unobserved results; queries concern Murray v. UBS and Rule 10, not this petition) and CourtListener lookups of Murray (601 U.S. 23). The one legible retrieved_doc_date (2026-04-29) predates resolution. Nothing in the log or prose shows this petition's disposition; the reasoning treats the conference as still future. Graded `not_applicable`; `leakage_suspected` = false.

## Big case

My own read is 0.03: an individual, self-represented employment dispute resolved below on threshold pleading grounds, with no split, no amicus interest and no writing at denial.
