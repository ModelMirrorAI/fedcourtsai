# Evaluation — gemini-baseline — scotus/73372297 / evt-petition-disposition

## The cell

Cert stage (`event.yaml` `stage: cert`, moment `distribution`, opened 2026-05-20).
Outcome: `actual_disposition: denied`, `actual_granted: 0`, resolved 2026-10-05
after the September 28, 2026 conference, one distribution, no CVSG, no noted
dissent. No `record/opinion/` slot is staged; a cert cell declares no semantic
set, so no `semantic_grades` block is written.

## What the prediction got right

- `predicted_disposition: denied` → `correct = 1`.
- `probability = 0.001` → `brier_score = 0.001² = 0.000001`, the lowest of the
  three candidates on this cell.
- Its one-paragraph forecast (summary denial at the first conference, no
  relist, no CVSG, no writing) matched the realized docket. The claims block
  and the forecast document are not scored here.

## Segment base rate and skill

The prediction froze `band: baseline` under `salience_version: sal-v4`, matching
the statpack table heading, so the basis is `risk_set` and the figure is the
bracketed `reached` rate pooled over the rendered Terms strictly before 2025
(2017–2024, all the pack holds within the ten-Term lookback):

| quantity | value |
| --- | --- |
| pooled weighted resolved (n) | 11,580 |
| `segment_base_rate` | 0.051209 |
| `brier_skill_score` | 1 − 0.000001 / 0.051209² = 0.99962 |

No version mismatch, no rendered-window divergence.

## Reasoning quality: 0.52

The direction is right and the conclusion is sound: the petition is, on any
reading, outside the grantable population, and the candidate says so. But
`reasoning_quality` grades the soundness of the analysis, and this one is thin
in ways that matter:

- **The anchor is the wrong row.** The reasoning says "the prior-Term `baseline`
  bracketed `reached` rate is 3.9%". That figure is the 2025 row of the sal-v4
  table, and 2025 is this case's own Term (`context.term: 2025`): the
  predict contract pools the rows strictly before the case's Term, which gives
  about 5.1% over 2017–2024. On a forward cell the practical harm is nil (the
  discount to 0.1% swamps it), but reading the case's own Term row as "prior"
  is exactly the self-selection error the per-Term table exists to prevent,
  and the reasoning gives no sign the candidate knew which row it was on.
- **The discount is stated, not argued.** Going from 3.9% to 0.1% is a factor of
  about forty, justified by "manifestly frivolous" and the SG's waiver. Both
  observations are correct, but the reasoning does not engage the one legal
  fact that actually decides this petition's posture: the Federal Circuit
  affirmed on an untimely motion for review, so even a charitably reframed
  question has no vehicle. The petition's own "The Appeal" section discloses
  this and the candidate read the petition's questions presented but, on the
  log, never opened `petition.txt` itself.
- **Hedged facts the record settles.** "Pro se-style petition": the snapshot's
  attorney block lists counsel only for the respondent, so the petitioner is
  pro se, not pro se-style. Small, but it signals the record was skimmed.
- **Calibration habit.** Writing a hard 0.0 on the CVSG increment is a claim
  matter, not graded here, but the same instinct shows in the prose: the
  reasoning asserts certainties ("will be summarily denied", "no Justice will
  dissent") where the other candidates argue probabilities. The outcome bore
  it out this time; the analysis would read identically on a cell where it did
  not.

What it does well: it identifies the respondent's waiver as a signal, notes
correctly that a CVSG is structurally inapplicable when the federal government
is already a party, and gets the summary-route logic right.

## Leakage

`mode: forward`. The log carries 20 calls, all `unobserved` (coverage 0.0),
which is this engine's standing telemetry shape rather than a defect, so each
call is graded on its query: reads of `AGENTS.md`, the predict prompt,
`context.json`, the 2026-09-16 snapshot, the document manifest, the questions
presented, the statpack, and the prediction schema, followed by its own output
writes. No corpus query, no web search, no CourtListener call, and no
`retrieved_doc_date` anywhere. The prediction was created 2026-09-16, before
the conference and the denial, and the reasoning treats the disposition as
future. Nothing suggests a decided case was provisioned forward.
`retrieved_outcome_material = false`, `influenced_prediction = not_applicable`,
`leakage_suspected = false`. Because every call is unobserved, this grade rests
on the queries and the reasoning rather than on observed results; the queries
are all provisioned-input reads, so that is enough.

## Stakes

My own read: `evaluator_score = 0.02`. A single claimant's Vaccine Act damages
dispute with no legal question; consequence beyond the parties is negligible.
