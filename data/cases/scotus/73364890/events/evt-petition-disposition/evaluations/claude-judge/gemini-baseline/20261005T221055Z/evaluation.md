# Evaluation of gemini-baseline — F.E.B. Corp. v. United States, No. 25-1294

**Outcome.** Petition denied on the 2026-10-05 order list after a single distribution for the 2026-09-28 conference; no CVSG, no relist, no noted dissent. `actual_granted` = 0.

**Prediction.** `denied`, P(grant) = 0.01. Correct on the disposition axis.

## Scores

| field | value | how |
| --- | --- | --- |
| correct | 1 | `denied` == `denied` |
| brier_score | 0.0001 | (0.01 − 0)² |
| segment_base_rate | 0.0512 | baseline band, bracketed `reached` figure, sal-v4 table in `metrics/statpack.md`, pooled resolved-weighted over Terms 2017–2024 (592.9 / 11,580 = 0.051203, held as 0.0512) |
| base_rate_basis | risk_set | the prediction froze `band: baseline` under `salience_version: sal-v4`, and the table heading names sal-v4 |
| brier_skill_score | 0.961853 | 1 − 0.0001 / (0.0512)² |
| reasoning_quality | 0.62 | see below |

The case's Term is 2025; the table renders 10 of 10 Terms, and the strictly-prior rows with a baseline figure are 2017–2024, so the rendered window and the pack's window coincide and no window divergence needs flagging. This is a cert cell, so Brier, rate, basis and skill are mine; `correct` is also written per contract for the stamp's comparison. No `vote_accuracy` (cert stage), no `semantic_grades` (no declared set), no `claim_scores` (harness-computed).

## What the reasoning got right

- It anchored on the right table and the right rows: the baseline band's prior-Term figures before Term 2025, quoted as a 4.5–5.9% range, which is the per-Term spread of the bracketed reached figures the pooled rate sits inside.
- It identified the decisive signal, the Solicitor General's June 16 waiver, and drew the right inference: a waived paid petition distributed without a call for a response is almost always denied at its first conference. That alone carries most of the distance from 5% to 1%.
- Its characterisation of the questions presented as a narrow, technical standard-of-review dispute under Rule 52(a) in a Submerged Lands Act case is accurate, and it correctly rules out a CVSG because the United States is already a party.
- The relist and dissent reasoning is consistent with the headline and with how the long conference disposes of such petitions.

## Where it is weaker

- The rationale is two paragraphs and never engages the petition or the Eleventh Circuit's opinion. It does not say what the petition argues, whether it pleads a split, how the panel applied Anderson, or what makes the vehicle poor. The conclusion is right, but the document gives a reader no way to check it against the record beyond the docket entries.
- It quotes a range rather than pooling the rate, so a reader cannot see which figure it adjusted from. The range is the correct one, so this costs clarity rather than accuracy.
- "The lack of an opposition brief further limits the likelihood" restates the waiver as if it were a second signal; it is the same fact. The sentence that the waiver "indicates the government believes the petition has no reasonable chance" is an overstatement of what a waiver communicates, though the practical inference drawn from it is right.
- The companion retrieval note says no retrieval beyond the provisioned inputs, while the captured log shows two general corpus queries. That is a disclosure gap in the cell's own record, not in the rationale, and I note it here without pricing it into `reasoning_quality`.

`reasoning_quality` 0.62: the key inference is correct and the number well placed, but the analysis is thin and does not demonstrate engagement with the record that the other two documents show.

## Leakage

Mode `forward` per the captured log. The prediction was created 2026-09-17 against the 2026-09-16 snapshot; the petition was resolved 2026-10-05. Every call in the log is `unobserved` (coverage 0.0, the engine's standing shape), so each is graded on its query. The two external calls are general `fedcourts query` invocations bounded by `--decided-before 2026-09-17`, one filtered to denials, neither naming this case; the rest are local reads of the provisioned record, the statpack, and the schema, then file writes and validation. Nothing suggests the case was decided when provisioned. `influenced_prediction` = `not_applicable`, `retrieved_outcome_material` = false, `leakage_suspected` = false.

## Big case

My independent read is 0.08: a local quiet-title dispute with a procedural question the Court settled forty years ago, no amicus, a government waiver, and a silent denial.
