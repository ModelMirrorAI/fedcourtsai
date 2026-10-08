# Evaluation of gemini-baseline — scotus/9026000121, evt-petition-disposition

**Cell.** Cert stage (`event.yaml` `stage: cert`, `moment: distribution`), Term
2026 by docket number (No. 26-121). Outcome: petition **denied** on
2026-10-05 after a single distribution for the September 28, 2026 conference,
with no noted dissent. Forward mode. No `record/opinion/` slot, the ordinary
state on a cert cell; no semantic set is declared, so no `semantic_grades`
block is written.

**Scores.**

| Field | Value | How |
| --- | --- | --- |
| `correct` | 1 | `predicted_disposition` `denied` matches `actual_disposition` `denied` |
| `brier_score` | 0.000001 | (0.001 − 0)² |
| `segment_base_rate` | 0.0501 | `baseline` band, bracketed `reached` figures, Terms 2017–2025 |
| `base_rate_basis` | `risk_set` | prediction froze `band: baseline` with `salience_version: sal-v4` |
| `brier_skill_score` | 0.9996 | 1 − 0.000001 / 0.0501² |
| `reasoning_quality` | 0.45 | below |
| `leakage_suspected` | false | forward cell, log clean (below) |

**Baseline.** Same computation as for the other candidates on this cell: the
frozen context carries `band: baseline` under `sal-v4`, matching the statpack
table's heading, so the risk-set basis applies. The `baseline` column's
bracketed `reached` rates, weighted by their bracketed `n`, pooled over the
rendered Terms strictly before 2026 (2017 through 2025), give 0.0501 over a
weighted n of 12,720. The caption renders 10 of 10 Terms, so the rendered
window is the pack's whole window; no divergence from the configured lookback
to flag. Pooled from rounded percentages, so approximate in the fourth decimal.

**What the prediction got right.** The disposition, and with the lowest
probability of the three (0.001), which against a denial yields the best Brier
and skill on the cell. That is the number's merit; the question for
`reasoning_quality` is whether the rationale earned it.

**Reasoning quality (0.45).** The rationale is a single paragraph. Its core
observations are correct and relevant: the petition sits at its first
distribution, the respondents waived, the Court almost never grants without
first calling for a response, the two questions (a Caperton-type judicial
qualification claim and a state statutory fee issue) present no developed
conflict, and the case is in the `baseline` band. Those are the right signals
and they point the right way.

What holds the grade down:

- **The anchor is asserted, not stated.** The write-up names the band but
  never states the band's rate or the pooling it used; it says a corpus query
  on "modern SCOTUS priors" confirms a very low grant probability for baseline
  petitions. The log shows that query was `fedcourts query --court scotus
  --limit 5` after an `--era modern` attempt. Five rows cannot confirm a
  base rate, and the committed statpack, which the prompt names as the
  anchor, is not mentioned. The claim overstates what the tool call showed.
- **The discount is not argued.** 0.001 is fifty times below the band's
  pooled rate. Some discount is warranted (state origin, waiver, no split),
  but nothing in the paragraph explains why this petition should sit at the
  floor of the band rather than merely well below its mean, and no residual
  for a summary judicial-bias correction is considered.
- **No engagement with the record.** The rationale does not reach the
  petition's actual posture: the intermediate court's evidentiary ground, the
  Maryland Supreme Court's Rule 8-602 dismissal, the fact that Question 2 rests
  on a state decision the Court cannot GVR against, or the unresolved timing of
  the judge's employment. All of it is in the provisioned petition and the
  other candidates found it. The analysis would read identically for most
  waived baseline petitions.

The direction and the main heuristic (waiver plus first distribution) are
sound, and the number was well placed, so the grade is in the middle rather
than the bottom. It is not higher because a rationale that neither states its
baseline nor touches the case-specific record is thin evidence that the
probability was reasoned rather than reflexive.

**Leakage.** Forward cell; the log records `mode: forward` with a
`result_capture_coverage` of 0.0, meaning every one of the 25 marker-carrying
calls is `unobserved`. That is this engine's standing telemetry shape, not a
defect and not evidence of anything; per the marker rule each call is graded
on its query alone and none is credited as having returned nothing. The
queries are reads of the prompt, AGENTS.md, event.yaml, context.json,
documents.json, the 2026-10-04 snapshot and questions-presented.txt, two
`fedcourts query --court scotus` corpus calls, the output file writes, and
`fedcourts validate data`. No CourtListener or web call; no query names this
petition's number, caption, or outcome; nothing under `data/qp-topics/`. The
rationale reads the pre-decision docket and does not presuppose the denial.
The prediction's snapshot (2026-10-04) predates the resolution, so this is not
a mis-provisioned decided case. `retrieved_outcome_material` false,
`influenced_prediction` `not_applicable`. Because the results were never
observed, this clean grade rests on the queries and the prose rather than on
observed results.

**Big case.** My own read is 0.05, for the reasons given in the companion
write-ups: a private Maryland fee dispute with an unresolved-fact Caperton hook,
denied silently on the first conference. The predictors' `big_case_score`
values were visible in the staged `prediction.json` I read for the
probabilities, so the read is independent in substance but not strictly blind.

**Not scored here.** The `claims` block and `predicted_reasoning.md` are the
harness's and were read for context only; `vote_accuracy` is omitted on a cert
cell by rule.
