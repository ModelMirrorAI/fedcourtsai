# Evaluation of codex-baseline — scotus/73286453, evt-petition-disposition

**Cell:** cert stage (`event.yaml` stage `cert`), forward mode. **Outcome:** petition denied on 2026-10-05, the order list after the September 28, 2026 conference; one distribution, no relist, no CVSG, no noted dissent (`outcome.json`: `actual_disposition` `denied`, `actual_granted` 0, `noted_dissent_from_denial` false).

## Scores

| Field | Value | How |
| --- | --- | --- |
| correct | 1 | `predicted_disposition` `denied` matches `actual_disposition` `denied` |
| brier_score | 0.0049 | (0.07 − 0)² |
| segment_base_rate | 0.0512 | `baseline` band, bracketed `reached` figure, pooled over Terms 2017–2024 (below) |
| base_rate_basis | risk_set | the prediction froze `context.band` `baseline` with `context.salience_version` `sal-v4`; the statpack table heading is `sal-v4` |
| brier_skill_score | −0.8690 | 1 − 0.0049 / (0.0512 − 0)² |
| reasoning_quality | 0.80 | below |
| vote_accuracy | omitted | cert stage; never scored here |

**Base rate.** The prediction's frozen context carries both `band` = `baseline` and `salience_version` = `sal-v4`, and the committed `metrics/statpack.md` table "Segment base rate by salience band (sal-v4)" names the same version, so the basis is `risk_set` and the figure is the bracketed `reached` rate. The case's Term is 2025 (`context.term`, docket 25-1242). The table renders Terms 2026 through 2017 ("Most recent 10 of 10 Term(s)"); 2026 is empty and 2025 is the case's own Term, so the pool is the eight prior Terms 2017–2024, weighted by each row's bracketed `n`: 592.9 grant-family outcomes over 11,580, or 5.12%. The configured in-code lookback is ten Terms, but the pack holds no rows before 2017, so the rendered window and the code's window coincide and there is no divergence to flag. The rate is computed from the table's rounded percentages, so it is approximate to a few hundredths of a point. The candidate computed the same pooled figure (5.12% over 11,580) and used it as its anchor.

## What the prediction got right and wrong

The headline was right and the forecast's shape matched the event: denied, most likely without a writing, after the September 28 conference. The 0.07 is the highest of the three numbers, so on a silent denial it carries the most negative skill; the gap between 0.07 and the 0.0512 anchor is small, and one denial cannot show whether the modest upward adjustment was miscalibrated. The question is whether that adjustment was reasoned.

Mostly yes. The candidate anchored correctly on the reached rate, read the statpack's relist and CVSG cuts correctly as terminal descriptions rather than forward multipliers, and grounded its case reading in the documents: the petition's argument section and appendix, the opposition's preservation argument and reproduced appellate-brief passages, Judge Jordan's dissent at appendix 17a, and the majority's treatment of Browder at appendix 9a–12a. It verified the two precedents the petition leans on by reading Lewis footnote 13 and Browder's clearly-established discussion on CourtListener rather than taking the petition's characterization. Its three offsetting features are the right ones: the panel assumed a violation and resolved only notice, so there is no clean holding to review; preservation is a concrete obstacle that the majority's own description of petitioner's theory supports, held at the right strength given the unprovisioned reply; and the unresolved color-of-law element flagged in Chief Judge Pryor's concurrence means even a win on immunity leaves a distinct question. It was candid about limits, including not refreshing the corpus or reading the reply.

Where it is a step behind the strongest analysis: it treats the "substantial tension with Browder and the Fourth Circuit decision" as a reason to move up without testing how deep the asserted split is, and it does not weigh the Court's doctrinal direction on substantive due process or the absence of institutional or amicus interest, both of which bear on a baseline-band grant prospect. The net move from 5.12% to 7% is small and the candidate says so, but the reasons listed for moving up (serious conduct, divided decision, tension with other circuits) are the generic features of many denied qualified-immunity petitions, and the write-up does not explain why they outweigh the three vehicle defects it identified so carefully. The summary-route conditional of 15% is defensibly reasoned from those same defects. The forecast document and claims are not scored here.

## Leakage

Forward mode, and the case was genuinely open: the prediction was created on 2026-09-16, the first conference was 2026-09-28, and the denial came on 2026-10-05. The log carries 30 calls at coverage 0.93: the two unobserved rows are hosted web searches whose queries target the Lewis citation and footnote and the Browder citation, not this petition, so graded on their queries they are clean (the candidate reports they returned nothing usable). Captured CourtListener calls resolved Lewis (523 U.S. 833) and Browder (787 F.3d 1076) by citation and read snippets of each on "intentional misuse" and "clearly established". There was no search for this docket, its caption, its subsequent history, or opinions citing the decision below, and nothing under `data/qp-topics/`. The reasoning states no prior knowledge of the disposition and that no target outcome material was encountered. `retrieved_outcome_material` false, `influenced_prediction` `not_applicable`, `leakage_suspected` false. The candidate's own `flags.json` is not staged, so this rests on the log and the prose.

## Big case

My own read, formed from the record before weighing the candidate's: 0.22. A private section 1983 suit over a fatal off-duty drunk-driving crash, decided below on the clearly-established prong with a divided published opinion. Some public resonance on police accountability, but interlocutory, fact-bound, clouded on color of law, with no amici or government interest, and denied silently.
