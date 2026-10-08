# Evaluation: gemini-baseline — scotus/73303792, evt-petition-disposition

**Cell.** Cert stage (`event.yaml` stage `cert`, moment `distribution`), forward
mode. Outcome: petition **denied** on 2026-10-05 at its first and only
distribution (conference of 2026-09-28), no separate writing, no CVSG.

## Scores

| Field | Value | How |
| --- | --- | --- |
| `correct` | 1 | `denied` vs `denied`, exact label match |
| `brier_score` | 0.0001 | (0.01 − 0)² |
| `segment_base_rate` | 0.05121 | baseline band, sal-v4, risk-set pool (below) |
| `base_rate_basis` | `risk_set` | frozen `context.band` + `context.salience_version` both present |
| `brier_skill_score` | 0.9619 | 1 − 0.0001 / (0.05121 − 0)² |
| `reasoning_quality` | 0.55 | below |

**Base rate.** The prediction's frozen context carries `band: baseline` and
`salience_version: sal-v4`; the statpack's "Segment base rate by salience band
(sal-v4)" heading matches, so the bracketed `reached` figures are the right
population. Pooling resolved-weighted over every rendered Term strictly before
Term 2025 (OT2017–OT2024, eight rows) gives 593 / 11,580 = 0.05121, reproduced
from `statpack.json`. The table renders 10 of 10 Terms, so the rendered window
is the pack's whole window and no divergence from the shipped lookback needs
flagging.

## What the prediction got right and wrong

Right where it counts: denial, at 1%, well under the band rate, earning most of
the available skill. Among the three candidates it is the least aggressive
number, which costs it a little Brier but is not unreasonable for a one-paragraph
analysis.

## Reasoning quality (0.55)

The rationale is a single paragraph that reaches the right conclusion by the
right route in outline: baseline band, pro se, section 1983 against local
judges and court officials, response waived, Court rarely grants without
calling for a response, no vehicle-worthy split. Every one of those statements
is true of this petition and each is a legitimate discount.

But it is thin in three ways that matter for the score. First, the anchor is
"roughly 5.5%", which is not the pooled strictly-prior reached rate for the band
(5.1%) and is not attributed to any row or window; it reads like a single
recent Term's figure or a rounded guess. Second, the candidate never engages
the petition's own content: which authorities it claims are split, whether the
Sixth Circuit's disposition was published, what the alternative grounds below
were, or that the petitioner had already lost a prior cert petition on the same
dispute. The record carried all of that and the stronger candidates used it.
Third, there is no statement of what was read or of any limit on the analysis
(OCR, missing appendix, no opposition), so a reader cannot tell how much of the
record the number rests on. The result is a correct instinct, soundly
expressed, with little analysis behind it.

## Leakage

Mode `forward`; `retrieved_outcome_material` false; `influenced_prediction`
`not_applicable`; `leakage_suspected` false. The prediction was created
2026-09-16 against the same-day snapshot (last entry the June 17
distribution); the denial came on October 5, so the case was open and the cell
was not mis-provisioned. The log's `result_capture_coverage` is 0.0, so every
call is graded on its query alone: the prompt, `AGENTS.md`, the provisioned
record, snapshot and documents, the statpack, and the schemas, followed by the
output writes and a validate. No web, MCP, or corpus call appears, and the
candidate's `retrieval.md` says the same. Nothing touches this petition's own
disposition or `data/qp-topics/`. Because no result was captured, a clean
reading here rests on the queries and the reasoning, not on any observed
absence of results.

## Big case

My independent read is 0.03 (see `evaluation.json`): a pro se custody-related
civil-rights suit against immune judicial officers, affirmed without opinion
and denied without comment. Nothing turns on it beyond the parties.
