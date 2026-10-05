# Retrieval log

Forward cell; retrieval unrestricted. Nothing consulted touched this
petition's own disposition. Total: 1 corpus query, 2 CourtListener MCP
searches, 2 CourtListener MCP endpoint calls.

## Corpus

- `uv run fedcourts query --court scotus --era 2020s --limit 12`
  stderr: `ranged corpus reads: 6 GET(s), 1572864 byte(s)`
  Returned 12 recent SCOTUS rows ranked by recency (mostly 26A applications
  and two OT2025 grants); none a useful comparator for a pro se paid petition,
  so not retried with sparser filters.

## CourtListener MCP

1. `search` type `o`, court `ca4`, q `Adkins Rosslyn Syndicate` — 0 results
   (the Fourth Circuit's unpublished per curiam is not in the opinion index).
2. `search` type `d`, q `Adkins Rosslyn Syndicate` — found the district court
   docket (vaed 1:25-cv-02117, docket id 71978608, filed 2025-11-20, nature of
   suit "890 Other Statutory Actions") and the Fourth Circuit docket (25-2451,
   docket id 72000778).
3. `call_endpoint` `docket-entries` for docket 71978608 — 32 entries. Confirms:
   leave to file an emergency complaint and an emergency injunction denied and
   case closed 2025-12-03; second motion for leave denied 2025-12-10; CA4
   unpublished affirmance 2026-03-30; rehearing en banc denied 2026-04-21 with
   no judge requesting a poll (panel Richardson, Berner, Floyd); mandate
   2026-04-29; CA4 order of 2026-08-04 enjoining the petitioner from further
   civil filings in that court absent certification.
4. `call_endpoint` `docket-entries` for docket 72000778 — 6 entries with
   empty descriptions; nothing usable.

## Statpack

- `metrics/statpack.md`: "Modern discretionary-cert petitions by
  disposition"; "Cert petitions by relist count (paid scored segment)"; "Cert
  petitions by CVSG status (paid scored segment)"; "Cert petitions by salience
  band"; "SCOTUS cert petitions by Term" and its "Segment base rate by
  salience band (sal-v4)" subtable.

No web searches.
