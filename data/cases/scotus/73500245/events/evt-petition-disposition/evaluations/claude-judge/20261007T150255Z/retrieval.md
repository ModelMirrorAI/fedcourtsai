# Retrieval log — claude-judge, scotus/73500245 / evt-petition-disposition / 20261007T150255Z

Provisioned inputs read: `event.yaml`, `outcome.json`, `record/context.json`, `record/snapshots/2026-10-05.json`, `record/documents/{documents.json,questions-presented.txt,petition.txt}`, and every file under `record/blinded/candidate-{a,b,c}/` (prediction.json, reasoning.md, predicted_reasoning.md, retrieval.md, retrieval_log.json). No `record/opinion/` slot was staged (expected on a cert cell). Nothing under `data/qp-topics/` was read, and the committed `predictions/` tree was not read.

## Committed base rates

- `metrics/statpack.md`, "Segment base rate by salience band (sal-v4)": baseline bracketed `reached` figures and `n` for OT2017–OT2024 (10 of 10 Terms rendered).
- `metrics/statpack.json`: the same per-Term baseline segments (`prefix_est_grant_rate`, `prefix_weighted_resolved`) for the unrounded pool — 593 / 11,580 = 0.051209 — and the "Petitions by originating court" bucket for the Supreme Court of Alabama (29 resolved, 28 denied, 1 granted), to check a figure claude-baseline cited.

## Corpus lookups

None. No `fedcourts query` or `open-events` call was made, so no `ranged corpus reads:` line was produced.

## CourtListener MCP lookups

1. `call_endpoint` endpoint `opinions`, query `{"cluster": 10761703, "fields": ["id","type","author_str","plain_text"]}` — returned the Alabama Supreme Court per curiam in *Blevins v. Alabama State Bar*, SC-2024-0693 (Rel. Dec. 19, 2025; opinion id 11228288). Purpose: verify claude-baseline's characterization of the decision below (statute held inapplicable to the Rule 1.4/1.5 charges; *Brooks* distinguished; no federal fair-notice analysis; five justices concurring in result, two recused) for the `reasoning_quality` grade. Not used for any new case fact and not a text graded against — this cert cell has no semantic set.

## Web searches

None.
