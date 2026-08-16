# Retrieval log

Beyond the provisioned snapshot, event definition, context, and the committed
`metrics/statpack.md`:

## CourtListener MCP (4 calls)

1. `search` (type `o`, q "Acosta-Tapia", court ca9) — looked for the Ninth
   Circuit opinion under review. No 2026 hit (older unrelated cases only).
2. `search` (type `o`, docket_number "25-2460", court ca9) — 0 results; the
   memorandum disposition is not in the opinions index.
3. `search` (type `d`, docket_number "25-2460", court ca9) — found the docket:
   *Acosta-Tapia v. Bondi*, CA9 25-2460, filed 2025-04-16, docket_id 72369758.
4. `call_endpoint` (`docket-entries`, docket 72369758, newest first, 15
   entries) — the disposition trail: memorandum disposition 2026-01-15
   (Hawkins, Rawlinson, Bress) — PETITION DISMISSED, stay of removal kept in
   place until mandate; submitted on the briefs without oral argument
   (2026-01-08); NILA out-of-time amicus in support of petitioner denied
   (2025-12-18); panel rehearing denied 2026-02-26.
5. `search` (type `rd`, docket_number "25-2460", q "memorandum") — both the
   memorandum and the rehearing petition show `is_available: false`, so
   neither document's text could be read. (5 calls total counting this one.)

## Corpus tooling (1 call)

- `uv run fedcourts query --court scotus --era 2020s --limit 8`
  `ranged corpus reads: 4 GET(s), 1048576 byte(s)`
  Returned recent resolved SCOTUS rows (mostly substantive applications and
  unrelated cert denials); confirmed the modal denial outcome but carried no
  case-specific signal, and did not move the number.

## Web searches

None.
