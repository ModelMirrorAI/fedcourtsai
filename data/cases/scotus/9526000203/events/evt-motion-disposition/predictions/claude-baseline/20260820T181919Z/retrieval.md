# Retrieval log — claude-baseline, 26A203, run 20260820T181919Z

Beyond the provisioned snapshot, event, and context, I consulted:

## Committed statpack

- `metrics/statpack.md`, "The interim docket (applications)" section — the
  strictly-prior pool for a Term-2026 cell (Terms 2025 + 2024: 225 resolved
  substantive, 30 granted, 13.3%) and the escalation-signal shape.

## Corpus (`fedcourts query`)

1. `uv run fedcourts query --court scotus --include-applications --query "…" --limit 8`
   — errored (`--query` is not an option); no corpus read.
2. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 10`
   — stderr: `ranged corpus reads: 32 GET(s), 8388608 byte(s)`. Returned
   recent granted cert petitions, not applications; used only as light
   context, no anchor taken from it.

## CourtListener MCP

1. `search` (type `d`, court `cadc`, docket_number `26-5123`) — located the
   underlying D.C. Circuit case (docket id 73204895, filed 2026-04-16,
   APA/Review Agency).
2. `call_endpoint` (`docket-entries`, docket 73204895,
   `date_filed__lte: 2026-08-14`) — the lower-court procedural history the
   stay application targets: the 2026-08-07 split per curiam judgment
   affirming the modified preliminary injunction, vacating the April 17
   administrative stay, staying the ruling fourteen days, mandate set for
   2026-08-21; briefing, argument (2026-06-05, Millett/Rao/Garcia), and
   circuit amici. Deliberately date-bounded to on/before 2026-08-14 so this
   case's own SCOTUS disposition could not surface; nothing outcome-revealing
   did.

No web searches. Total: 2 MCP calls, 2 corpus command attempts (1 successful).
