# Evaluation of codex-baseline — scotus/73281633, evt-petition-disposition

**Cell:** cert stage, forward mode. **Outcome:** petition DENIED on 2026-10-05 after a single distribution (Conference of 9/28/2026), no CVSG, no relist, no noted dissent (`actual_granted` = 0, `disposition_basis` standard).

## Scores

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.09 − 0)² = 0.0081.
- `segment_base_rate` = 0.0512, basis `risk_set`. The prediction froze `band: baseline` under `salience_version: sal-v4`, and the committed `metrics/statpack.md` table "Segment base rate by salience band (sal-v4)" carries the same version, so the bracketed `reached` figure applies. Pooled resolved-weighted over the rendered Terms strictly before OT2025 (2017–2024, eight rows: 4.7, 4.6, 4.6, 4.5, 5.6, 5.8, 5.9, 5.7 % on n = 1643, 1524, 1399, 1739, 1500, 1192, 1312, 1271) gives 593 / 11,580 ≈ 5.12%. The caption states the table renders 10 of 10 Terms, so the rendered window is the pack's whole window and no lookback divergence arises.
- `brier_skill_score` = 1 − 0.0081 / 0.0512² = −2.09. Negative: the petition was denied and the forecast sat above the baseline, so the naive base-rate forecast beat it. This is the expected shape for any uplift on a denied baseline-band petition; of the three candidates this one carried the smallest uplift and so the least negative skill.
- No `vote_accuracy`, no `semantic_grades`: cert stage.

## Reasoning quality: 0.82

What drove the score up:

- Base-rate work is exactly right: the sal-v4 table, the `reached` figure, resolved-weighted over 2017–2024, 593/11,580, and an explicit refusal to substitute the terminal relist and CVSG buckets for transition probabilities — the statpack caption's own warning, applied.
- The split analysis is read against the record, not the petition's framing. It credits the BIO's point that the circuits share the Edenfield framework and differ on their records, and it checks the reproduced Second Circuit opinion (Pet. App. 12a–15a) to find that the panel did cite studies and did consider the ingredients-based alternative — which makes the petition's "no evidence, no tailoring" characterization too strong. That is the right reading and it is the reason a denial was likely.
- The vehicle analysis is precise where the others are loose: it identifies the independent public-interest ground at 30a *and* notes that footnote 9 left the delay question unresolved, which is what the appendix actually says (the panel wrote that it "need not address" the five-month delay). It then declines to treat every equities point as airtight because the irreparable-harm analysis is partly derivative of the merits. That is careful, two-sided weighing.
- The uplift from 5.1% to 9% is stated as a modest judgment, with reasons (recurring question, four amici, several circuits named) and with the constraint (contested split, interlocutory posture) stated beside it. The calibration matched the outcome.

What held it back:

- A substantial share of the document is provenance and tooling narration (snapshot embedded dates, cache directories, failed web fetches of the Rules PDF). It is honest, but it is not legal analysis, and the forecast would read better with that moved to `retrieval.md`.
- It did not read the reply or the amicus briefs and says so; the forecast therefore leans on the BIO's characterization of the alternative grounds without checking whether the reply contests them. claude-baseline carries the same gap.
- The 28% relist estimate is defensible but not argued from anything beyond "serious but imperfect petition at first conference".

## Big case

My own read is 0.38 (see `evaluation.json`). I note for the record that the staged `prediction.json` carries the predictor's `big_case_score`, so I had seen the number before writing mine; my read was formed on the record and outcome rather than on it. codex-baseline's 0.59 is on the high side of what I would give an interlocutory, single-state, no-writing denial, but its rationale correctly names the doctrinal reach and the vehicle limits.

## Leakage

Forward cell, `influenced_prediction` = `not_applicable`, `leakage_suspected` = false. The prediction was created 2026-09-16; the denial came 2026-10-05. The captured log shows reads of the provisioned record and statpack and two uncaptured web-search rows whose queries seek the Court's Rule 10 text, not this case; no docket, corpus, or CourtListener lookups; no retrieved document dated at or after resolution. One `find` command names `data/qp-topics/` as a `-not -path` exclusion, which is the opposite of a read. The reasoning states that no outcome was known. I found no sign that a decided case was provisioned forward.
