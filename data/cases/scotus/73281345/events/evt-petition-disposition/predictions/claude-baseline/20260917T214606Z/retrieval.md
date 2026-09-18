# Retrieval log

Provisioned inputs read: `record/snapshots/2026-09-17.json`, `record/context.json`, `record/documents/documents.json`, `questions-presented.txt`, `brief-in-opposition.txt`, `petition.txt` (read in full by a delegated subagent that returned a structured summary), and `metrics/statpack.md` (modern-cert disposition, originating-circuit, relist-count, CVSG, salience-band, per-Term, and sal-v4 segment tables).

## Corpus lookups (`fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
   `ranged corpus reads: 28 GET(s), 7340032 byte(s)`
   Returned recent granted SCOTUS rows (mostly substantive applications and OT2025 grants). Recency-ranked, no topical match to the Commerce Clause question; used for shape only.
2. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
   `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm service cache)
   Returned recent denied rows (capital applications and a labor petition). Not comparable; shape only.

## CourtListener MCP lookups

1. `search` type=`d`, court=`scotus`, q=`Chavarria`, filed_after=`2025-06-01` — 0 results. Purpose: check whether the government sought certiorari in *United States v. Chavarria* (10th Cir. 2025), which could make this petition a hold candidate. Nothing found (consistent with the BIO's silence).
2. `call_endpoint` `docket-entries`, docket=`73281345`, newest first — 0 results. Purpose: confirm no docket movement after the provisioned snapshot. CourtListener carries no entries for this Supreme Court docket, so the snapshot (dated today) is the record.

No web searches. Nothing retrieved concerned this petition's disposition.
