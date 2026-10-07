# Evaluation of gemini-baseline — scotus/73286453, evt-petition-disposition

**Cell:** cert stage (`event.yaml` stage `cert`), forward mode. **Outcome:** petition denied on 2026-10-05, the order list after the September 28, 2026 conference; one distribution, no relist, no CVSG, no noted dissent (`outcome.json`: `actual_disposition` `denied`, `actual_granted` 0, `noted_dissent_from_denial` false).

## Scores

| Field | Value | How |
| --- | --- | --- |
| correct | 1 | `predicted_disposition` `denied` matches `actual_disposition` `denied` |
| brier_score | 0.0001 | (0.01 − 0)² |
| segment_base_rate | 0.0512 | `baseline` band, bracketed `reached` figure, pooled over Terms 2017–2024 (below) |
| base_rate_basis | risk_set | the prediction froze `context.band` `baseline` with `context.salience_version` `sal-v4`; the statpack table heading is `sal-v4` |
| brier_skill_score | 0.9619 | 1 − 0.0001 / (0.0512 − 0)² |
| reasoning_quality | 0.40 | below |
| vote_accuracy | omitted | cert stage; never scored here |

**Base rate.** The prediction's frozen context carries both `band` = `baseline` and `salience_version` = `sal-v4`, and the committed `metrics/statpack.md` table "Segment base rate by salience band (sal-v4)" names the same version, so the basis is `risk_set` and the figure is the bracketed `reached` rate. The case's Term is 2025 (`context.term`, docket 25-1242). The table renders Terms 2026 through 2017 ("Most recent 10 of 10 Term(s)"); 2026 is empty and 2025 is the case's own Term, so the pool is the eight prior Terms 2017–2024, weighted by each row's bracketed `n`: 592.9 grant-family outcomes over 11,580, or 5.12%. The configured in-code lookback is ten Terms, but the pack holds no rows before 2017, so the rendered window and the code's window coincide and there is no divergence to flag. The rate is computed from the table's rounded percentages, so it is approximate to a few hundredths of a point.

## What the prediction got right and wrong

The headline was right: denied, and at the first conference with no relist and no separate writing, which is exactly the modal path the candidate described. Its 0.01 also produced the best Brier of the three candidates on this denial.

The number is not well supported by the analysis, though. The reasoning identifies the correct anchor (the bracketed `baseline` reached rate, which it quotes as "around 4.5% to 6.0%") and then cuts it by a factor of five on two grounds. The first, that the petition "is currently at its first distribution (0 relists), and the vast majority of petitions that are not relisted are denied", misreads a terminal cut as a forward hazard: at the snapshot the petition had been distributed for its first conference and not yet considered, which is the state every petition in the risk set occupies before its first conference, so it carries essentially no information beyond what the reached rate already encodes. A relist count of zero before the first conference is not evidence of a denial on the way. The second ground, the preservation problem the brief in opposition raises, is real and the outcome is consistent with it mattering, but the candidate states it in the respondent's terms ("conceded below that no caselaw was directly on point") without checking it against the petitioner's own appellate brief reproduced in the opposition's appendix, and the log shows it read only the first fifty to one hundred lines of the petition and of the brief in opposition. It did not register that the decision below was a published opinion with a reasoned partial dissent, that the respondent filed a full opposition after an extension rather than waiving, or that the petition asserts a two-circuit conflict, all of which cut the other way and which the other candidates weighed.

So the analysis names one genuine vehicle problem, anchors correctly, and then overshoots on a misapplied statistic while leaving the upward factors unexamined. A denial at the first conference does not validate the magnitude of a 0.01 call; a baseline-band petition with a divided published opinion and full briefing is denied around 95% of the time, not 99%. The forecast document was read for context only and is not scored; the claims block is the harness's.

## Leakage

Forward mode, and the case was genuinely open: the prediction was created on 2026-09-16, the first conference was 2026-09-28, and the denial came on 2026-10-05. The captured log holds 28 calls, all file reads or shell reads of the provisioned record, the predict prompt, `AGENTS.md`, and the statpack, plus the candidate's own output writes and a validate run. No corpus query, no CourtListener call, no web search, and nothing under `data/qp-topics/`. Every call carries `result_capture` = `unobserved` (coverage 0.0), which is an engine's standing shape rather than a defect; graded on their queries, none reaches past the snapshot or toward this petition's disposition. The reasoning does not presuppose the outcome. `retrieved_outcome_material` false, `influenced_prediction` `not_applicable`, `leakage_suspected` false. The candidate's own `flags.json` is not staged, so this rests on the log and the prose.

## Big case

My own read, formed from the record before weighing the candidate's: 0.22. A private section 1983 suit over a fatal off-duty drunk-driving crash, decided below on the clearly-established prong with a divided published opinion. Some public resonance on police accountability, but interlocutory, fact-bound, clouded on color of law, with no amici or government interest, and denied silently.
