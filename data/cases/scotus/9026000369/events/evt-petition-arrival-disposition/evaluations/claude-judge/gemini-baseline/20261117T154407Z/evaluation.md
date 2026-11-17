# Evaluation — gemini-baseline, evt-petition-arrival-disposition (scotus/9026000369)

**Cell.** Cert stage, arrival moment: *Loop v. Washington*, No. 26-369. Outcome: petition **denied** on 2026-11-16 after one distribution (conference of 11/13/2026), all respondents having waived; no CVSG, no noted dissent.

**Scores.** Predicted `denied` at P(grant) = 0.001 → `correct` = 1, `brier_score` = 0.000001. No `vote_accuracy` (cert cell). The segment base rate, skill score and claim scores are the harness's to stamp; any comparison is against the stamped segment base rate. No semantic grades (cert cell, no declared set).

## Reasoning (`reasoning_quality` = 0.5)

The call (denied, P(grant) 0.001) was correct and earns the lowest Brier of the cell. The rationale, a single paragraph, names the right anchor (the baseline band's pooled arrival rate over prior Terms) and the two dominant downward factors (pro se petitioner; a collateral attack on a state family-law arbitration with no circuit split of national importance). That is directionally sound and the conclusion is right. But it is thin: the transcript shows only the first 50 lines of the petition were read, there is no engagement with the decision below, the petition's conflict claims, the unreviewability of QP2, or alternative grounds, and nothing explains why the adjustment is a factor of fifty rather than five or ten. A 0.1% figure on a paid petition is defensible here but is asserted rather than argued. Sound in direction, generic in support.

## Predicted reasoning (`predicted_reasoning_quality` = 0.55)

Central claims: no relist, no CVSG, a clean denial with no dissent or statement — all borne out. The document commits to little beyond the modal path for any long-shot petition: no forecast of respondents' behaviour, timing, or conference path. Its one distinctive premise, that there is no intervening Rooker-Feldman precedent, is conditional on a grant that never came and so is unresolved, though the petition itself discusses a June 2026 Rooker-Feldman decision, so the premise looks under-read. Right in direction but generic: just above the 0.5 anchor.

Checked against: Docket (2026-11-16 snapshot): waivers Oct 2 and Oct 8, DISTRIBUTED Oct 28 for Conference of 11/13/2026, 'Petition DENIED' Nov 16.

## Leakage

Mode `forward`; `influenced_prediction` = `not_applicable`, `leakage_suspected` = false. Forward cell, predicted 2026-09-27; event resolved 2026-11-16. Every call in the log is result-unobserved (coverage 0.0, the engine's standing shape), so it is graded on queries: reads of the provisioned record, statpack and the first 50 lines of the petition, and one fedcourts topical query on Rooker-Feldman/section 1983/family arbitration (not for this docket). No web search, no query for this case's caption or docket past the event date; the reasoning shows no knowledge of the outcome. Note the candidate's retrieval.md says no retrieval beyond provisioned inputs although the log shows the corpus query; that is a disclosure inaccuracy, not outcome material.

## Big case (evaluator read 0.12)

Paid petition, pro se at filing, from an unpublished CA9 memorandum affirming a Rooker-Feldman dismissal of a section 1983 suit arising from a privately arbitrated parenting plan. QP2 (delegating parental-rights adjudication to a private arbitrator) has some national family-law reach in the abstract and drew five cert-stage amicus briefs plus a later counsel appearance, but it was never reached below; all respondents waived, the petition was distributed once and denied without a writing.
