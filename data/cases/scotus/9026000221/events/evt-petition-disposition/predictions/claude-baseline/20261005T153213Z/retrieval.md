# Retrieval log

## Corpus lookups (`fedcourts query`, via the cell's corpus service)

- `uv run fedcourts query --court scotus --era 2020s --disposition granted`
  stderr: `ranged corpus reads: 43 GET(s), 11075584 byte(s)`
  Purpose: shape of recently granted paid petitions (distribution counts,
  originating courts). Top rows were OT2025 grants from the September 28,
  2026 conference; none was a Confrontation Clause case.
- `uv run fedcourts query --court scotus --era 2020s`
  stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm cache)
  Purpose: shape of first-distribution OT2026 petitions resolved at the
  long conference; the rows returned were October 5, 2026 denials.

## Committed base rates

- `metrics/statpack.md`: "Modern discretionary-cert petitions by
  disposition", "Cert petitions by relist count (paid scored segment)",
  "Cert petitions by CVSG status (paid scored segment)", "Cert petitions by
  salience band", "Petitions by originating court", "SCOTUS cert petitions
  by Term", and "Segment base rate by salience band (sal-v4)".
- `metrics/statpack.json`: the originating-court buckets for "Court of
  Appeals of Kansas" (11 resolved, all denied) and "Supreme Court of Kansas"
  (20 resolved, 3 granted), which the markdown table truncates.

## CourtListener MCP lookups (forward mode, unrestricted)

1. `search` type=d, court=scotus, docket_number=26-221 — 0 results (no RECAP
   docket for this case; nothing beyond the provisioned snapshot was found).
2. `search` type=o, courts ca1/ca2/ca5/ca6/ca7, filed after 2024-06-21,
   query on Smith v. Arizona plus course-of-investigation phrasing — 1
   result: Roalson v. Noble, 116 F.4th 661 (7th Cir. 2024). Not read further.
3. `search` type=o, court=kanctapp, filed after 2025-01-01, query Purdy
   confrontation 60-1507 — 0 results (the unpublished opinion below is not
   indexed; I used the copy in the petition appendix).
4. `search` type=o, court=ca6, filed after 2025-01-01, "Reed v. May" —
   1 result: Patrick Reed v. Harold May, 134 F.4th 455 (6th Cir. Apr. 11,
   2025), confirming the split-side decision the petition cites.
5. `search` type=o, court=ca1, filed after 2026-01-01, Cartagena +
   "Smith v. Arizona" — 1 result: United States v. Cartagena (1st Cir.
   Apr. 15, 2026), confirming the decision the petition cites.

No web searches. No lookup of this case's own disposition was made; the
docket search in item 1 returned nothing.
