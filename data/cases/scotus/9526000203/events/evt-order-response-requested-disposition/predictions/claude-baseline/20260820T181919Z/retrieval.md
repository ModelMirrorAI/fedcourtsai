# Retrieval log

Beyond the provisioned inputs (event.yaml, record/context.json, the 2026-08-15
snapshot) and the committed `metrics/statpack.md`:

## Corpus (`fedcourts` CLI)

1. `uv run fedcourts query --court scotus --include-applications --limit 10`
   — stderr: `ranged corpus reads: 4 GET(s), 1048576 byte(s)`.
   Returned ten recency-ranked application rows (one substantive denial,
   nine time-extension grants); not informative for this cell beyond
   confirming corpus vintage (`last_live_polled` 2026-08-19/20).

## CourtListener MCP

2. `search` (type `d`, court `cadc`, docket_number `26-5123`) — identified the
   D.C. Circuit appeal: *National Trust for Historic Preservation v. NPS*,
   filed 2026-04-16, APA/review-of-agency suit nature, docket id 73204895.
3. `search` (type `d`, court `dcd`, q `"National Trust for Historic
   Preservation"`) — identified the underlying district case: No.
   1:25-cv-04316 (Judge Richard J. Leon, filed 2025-12-12), plus unrelated
   older matters.
4. `call_endpoint` (`docket-entries`, docket 73204895, newest first, 15
   entries) — the decisive context: the August 7, 2026 per curiam judgment
   affirming the district court's modified preliminary injunction (opinion by
   Millett and Garcia, 101 pages; Rao dissenting, 35 pages), vacating the
   April 17 administrative stay, staying the ruling fourteen days for Supreme
   Court review, with the mandate reset to August 21; expedited merits argued
   June 5, 2026; amicus filings below by Members of Congress, the ACLU of
   D.C., and others.

No web searches. Retrieval was deliberately stopped after the lower-court
docket read to avoid surfacing this application's own disposition (the
response fell due August 18; prediction made as of the 2026-08-15 snapshot
state).
