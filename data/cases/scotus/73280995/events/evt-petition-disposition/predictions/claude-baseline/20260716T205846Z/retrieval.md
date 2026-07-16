# Retrieval log — scotus/73280995 / evt-petition-disposition / claude-baseline / 20260716T205846Z

Mode: `forward` (retrieval unrestricted). Beyond the provisioned snapshot,
QP, petition, and BIO, and the committed `metrics/statpack.md` (base rates):

## Corpus lookups (`fedcourts` CLI)

1. `uv run fedcourts query --court scotus --citation "Bivens v. Six Unknown Named Agents" --citation "Carlson v. Green" --citation "Egbert v. Boule" --limit 8`
   - stderr: `ranged corpus reads: 418 GET(s), 109576192 byte(s)`
   - Returned no rows.
2. `uv run fedcourts query --court scotus --citation "Carlson v. Green" --limit 8`
   - stderr: `ranged corpus reads: 418 GET(s), 109576192 byte(s)`
   - Returned no rows.

## CourtListener MCP lookups

3. `search` (type=d, court=scotus, docket_number=25-417) — no hits in the
   RECAP/docket search index.
4. `call_endpoint` (dockets, court=scotus, docket_number=25-417) — found
   *Francis Nielsen v. Kekai Watanabe*, CL docket 73278422, filed 2025-10-07,
   not terminated, no cert-granted/denied dates recorded (docket last
   modified 2026-06-22).
5. `call_endpoint` (docket-entries, docket=73278422) — zero entries in
   CourtListener for this SCOTUS docket.

## Web

6. WebSearch: `Nielsen v. Watanabe 25-417 Supreme Court cert petition Bivens
   Carlson` — surfaced the SCOTUSblog case page and a June 2026 SCOTUSblog
   article; indicated the petition was granted.
7. WebFetch: https://www.scotusblog.com/cases/nielsen-v-watanabe/ —
   confirmed **cert granted June 22, 2026** (OT2026), after distribution for
   the 6/11 and 6/18/2026 conferences (same conferences as this petition).
8. WebFetch: https://www.scotusblog.com/2026/06/bivens-at-the-bedside-/ —
   confirms Mohan (25-952) is discussed as the companion case in which the
   SG itself recommended granting *Nielsen* instead.

All lookups concerned the lead/companion case *Nielsen* and general context;
none sought this case's own disposition (none exists — the petition is
pending, held).
