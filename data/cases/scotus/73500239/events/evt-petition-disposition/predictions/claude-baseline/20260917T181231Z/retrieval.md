# Retrieval log

Forward cell; retrieval unrestricted. Five calls total (one corpus query, four CourtListener MCP searches). Nothing retrieved disclosed this petition's disposition.

## Corpus (`fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted`
   stderr: `ranged corpus reads: 47 GET(s), 12320768 byte(s)`
   Returned recent granted SCOTUS rows (largely substantive applications and government-side petitions with multiple distributions). Used only as a check on the shape of the granted population; no returned prior resembles a waived-response private First Amendment employment petition.

## CourtListener MCP (`search`)

2. `type=o, q="Pesta \"Cleveland State University\"", court=ca6, filed_after=2025-01-01` — 0 results.
3. `type=d, q="Pesta Bloomberg", court=scotus` — 0 results (the SCOTUS docket is not indexed).
4. `type=o, q="Pesta Pickering \"research misconduct\"", filed_after=2024-01-01` — 0 results (the unpublished Sixth Circuit opinion is not indexed).
5. `type=r, q="Pesta Bloomberg", court=[ca6, ohnd]` — 1 result: *Pesta v. Cleveland State University*, N.D. Ohio 1:23-cv-00546, filed 2023-03-16, terminated 2024-10-07 (docket id 67021659). Confirms the procedural history stated in the petition. Not opened further.

## Base rates

`metrics/statpack.md` (committed): "Segment base rate by salience band (sal-v4)", "Cert petitions by relist count (paid scored segment)", "Cert petitions by CVSG status (paid scored segment)", "Modern discretionary-cert petitions by disposition", "Modern cert petitions by originating circuit".

No web searches.
