# Evaluation: gemini-baseline, scotus/9026000352, evt-petition-disposition

**Outcome.** Cert-stage cell. The petition (No. 26-352, *Wray v. RTX Corporation*) was denied on November 16, 2026, after a single distribution for the November 13 conference; Justice Alito took no part. No CVSG, no relist, no noted dissent.

**Scores.** Predicted `denied` at P(grant) = 0.002: `correct` = 1, `brier_score` = 0.000004. The segment base rate, its basis and the skill score are the harness's to stamp and are left null here; claim scores are computed in code. No vote accuracy on a cert cell, and no semantic grades (no semantic set is declared at this stage).

## Reasoning (`reasoning_quality` = 0.82)

A sound and well-grounded rationale. It anchors on the frozen `baseline` reached rate, cross-checks several statpack marginals, and then gives four concrete case-specific reasons for a steep discount: a self-represented petition with rhetorical, non-doctrinal questions; an unpublished two-sentence per curiam affirming a Rule 12(b)(6) dismissal on settled threshold grounds (accurately itemised with the controlling authorities, including the state-versus-federal DOL exhaustion point and *Digital Realty*); no circuit split and a misplaced reliance on *Murray*, which the district court had cited and which goes to intent rather than exhaustion; and distribution with no response and no call for one. The Court's first-conference denial is exactly what this analysis predicts. Deductions: the marginal cuts are listed without the caution that they are terminal, overlapping categories; the statement that RTX "did not file a brief in opposition" is true of the docket but the write-up leans on it as if it were an affirmative signal; and the explanation of the conditional summary-route number is somewhat strained. The relist probability is rationalised mainly by clerical reschedules, which is thin but harmless.

## Predicted reasoning (`predicted_reasoning_quality` = 0.7)

Central claims: denial on the first conference list by a routine unsigned order on the Monday order list (November 16 was that Monday); zero further distributions; no CVSG; no dissent or statement. All borne out on the staged docket and outcome. The conditional reformulation/GVR/affirmance content never came into play and earns nothing either way. The forecast commits firmly ("will deny", "no Justice will note") and is specific on timing and form, but these were the heavily expected calls for this petition, so it sits just under the 0.75 anchor rather than at the top. Justice Alito's non-participation was not anticipated, a marginal detail.

## Leakage

Forward cell, genuinely open when predicted. Log mode forward; prediction created 2026-10-31, before the 2026-11-13 conference and the 2026-11-16 denial. Calls are provisioned-record reads, statpack reads and three corpus queries (recent SCOTUS rows, a 601 U.S. 23 citation check); no web or MCP lookups. Several late calls are outcome_only file writes of its own outputs. Nothing in the log or prose shows this petition's disposition; the reasoning treats the conference as still future. Graded `not_applicable`; `leakage_suspected` = false.

## Big case

My own read is 0.03: an individual, self-represented employment dispute resolved below on threshold pleading grounds, with no split, no amicus interest and no writing at denial.
