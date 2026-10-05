# Retrieval log

## Corpus (`fedcourts query`)

1. `uv run fedcourts query --court scotus --citation "570 U.S. 1"`
   stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   Result: no rows; the tool's note said only 200 SCOTUS rows carry any reporter
   citation, so the empty result reflects the sparse column, not a missing case.
   Not used.
2. `uv run fedcourts query --court scotus --disposition granted --era 2020s`
   stderr: `ranged corpus reads: 39 GET(s), 10223616 byte(s)`
   Result: recent granted/substantive SCOTUS rows (e.g. DHS v. D.V.D., People
   Not Politicians v. Onder, NRCC v. Brown); none concerned the NVRA or
   proof-of-citizenship. Read for shape only; no prior was relied on.

## Base rates

- `metrics/statpack.md`, section "The merits docket (granted cases)": pooled
  grant Terms 2017–2024 (the Terms rendered inside the 2015–2024 window) for a
  69.8% disturbed rate on 516 parsed judgments. See `reasoning.md`.

## CourtListener MCP

3. `search` (type `o`, court `ca9`, q `"Mi Familia Vota" "Fontes" citizenship NVRA`,
   filed after 2025-01-01): two hits, *Promise Arizona v. Petersen*, No.
   24-4029, filed 2025-02-25 (panel opinion) and 2025-09-22 (rehearing denial);
   the `judge` field was empty on both.
4. `call_endpoint` `opinions` id 10339077 (fields cluster/author_str/joined_by_str):
   author and joined-by fields empty; the cluster pointer returned did not match
   the case.
5. `call_endpoint` `clusters` id 9872467: resolved to an unrelated record
   (*Picard v. RAR Entrepreneurial Fund*). Abandoned the panel-composition lookup.

No retrieval touched this case's disposition; the case is pending and the
adverse respondents' merits briefs are not yet filed.

## Delegated reading of provisioned inputs

A subagent read `record/documents/petition.txt` and
`record/documents/brief-in-opposition.txt` in full and returned a structured
summary; I read `questions-presented.txt`, `merits-brief-petitioner.txt`,
`merits-brief-respondent.txt`, `documents.json`, the snapshot, `context.json`,
and `event.yaml` directly. Nothing under `data/qp-topics/` was read.
