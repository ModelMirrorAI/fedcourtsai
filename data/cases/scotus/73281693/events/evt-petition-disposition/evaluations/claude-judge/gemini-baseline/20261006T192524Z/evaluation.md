# Evaluation of gemini-baseline — scotus/73281693, evt-petition-disposition

**Cell.** Cert stage, forward mode. Outcome: petition **denied** on the 2026-10-05 order list after a single conference (2026-09-28), no relist, no noted dissent from denial, two distributions total (the second a redistribution after the June 2 call for response). Supplemental briefs from both sides were filed and distributed 2026-09-29.

**Prediction.** `denied`, P(grant) = 0.07.

## Scores

| field | value | how |
| --- | --- | --- |
| correct | 1 | `denied` == `denied` |
| brier_score | 0.0049 | (0.07 − 0)² |
| segment_base_rate | 0.1724 | `elevated` band, sal-v4, bracketed `reached` rate pooled resolved-weighted over Terms 2017–2024 (eight rows, 2810 weighted n) |
| base_rate_basis | risk_set | prediction froze `band: elevated` with `salience_version: sal-v4`; the statpack heading names sal-v4 |
| brier_skill_score | 0.8351 | 1 − brier / (base − 0)² |

The base rate is taken from the prediction's own frozen context, not from this cell's `record/context.json` (which, being provisioned from the decided docket, also reads `elevated`, but that is not the reason it is used). The statpack table renders all ten Terms the pack holds, so the pooled window is the pack's own; no window divergence to flag. The Term-2025 and Term-2026 rows are excluded.

## What the reasoning got right and wrong

The rationale is short and lands close to the realized outcome. It names the right anchor (elevated reached rate, about 17.5%), then moves down hard for two reasons that each held up: the Court's post-pandemic pattern of declining COVID-19 mandate vehicles, and respondent's Rule 56 / evidentiary objections that would entangle any merits ruling with the record. Both are the reasons a careful observer would give for this denial, and the silent, single-conference denial is consistent with a Court that saw the vehicle rather than the question.

What drags `reasoning_quality` down is what the document does not engage with. It never mentions the June 2 **call for response after a waiver**, the single strongest attention signal on the docket, nor the counsel of record, nor whether the two recorded distributions reflect a relist (they do not). It treats the amicus bloc only as the thing that produced the salience band, not as evidence in its own right. A rationale that omits the main upward evidence cannot be fully credited for a low number, even when the low number was right: the adjustment from 17.5% to 7% is asserted ("significantly") rather than argued through the competing signals. The circuit-split characterization (3-3) is taken from the petition without noting the brief in opposition's cross-citation argument that the split is contestable, which was the respondent's best point and the likeliest ground of denial.

Net: sound direction, correct emphasis on vehicle, thin engagement with the record. **reasoning_quality 0.60.**

## Leakage

Forward cell; prediction created 2026-09-18, petition denied 2026-10-05. The captured log (30 calls, every result marker unobserved, so each call is graded on its query) shows only reads of the provisioned record, the predict prompt, AGENTS.md, metrics/statpack.md, and grep slices of the petition and brief in opposition; no web, MCP, or corpus calls; no query reaches past the 2026-09-17 snapshot; no read under data/qp-topics/. Reasoning reads the case as pending. No outcome material retrieved. `influenced_prediction` = `not_applicable`, `leakage_suspected` = false. Note that the candidate's own `flags.json` is not staged, so the absence of a disclosure there is not evidence; the grade rests on the log and the prose.

## Big-case read

Independent read 0.55 (see `big_case.notes`): an important post-Groff statutory question carried by a lapsed-mandate record, denied silently.

## Not scored here

The forecast document and the `claims` block are the harness's (`claim_scores`); `vote_accuracy` is omitted on a cert cell; no semantic set is declared on a cert event, so no `semantic_grades` block is written.
