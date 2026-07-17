# Retrieval log — scotus/73248556 / evt-petition-disposition / claude-baseline / 20260717T180352Z

Forward-mode cell; retrieval unrestricted. Everything below predates or is
independent of this petition's own (nonexistent) disposition. ~18 retrieval
calls total, within the advisory budget.

## CourtListener MCP

1. `search` (opinions, court=scotus, q="Hemani", filed_after=2026-01-01) →
   *United States v. Hemani*, No. 24-1234, decided **2026-06-18**
   (cluster 10876933).
2. `call_endpoint` (clusters, id=10876933) → metadata only; syllabus empty.
3. `search` (opinions, q=`"Hemani" AND "judgment of the Court of Appeals" AND "affirmed"`) → 0 results.
4. `search` (opinions, q=`Hemani "court of appeals"`, filed_after=2026-06-01) → same cluster; no snippets returned.
5. `call_endpoint` (opinions, cluster=10876933) → opinion id 11344434 (39 pp., combined).
6. `search` (dockets, court=scotus, docket_number=25-935) → 0 results.
7. `call_endpoint` (dockets, court=scotus, docket_number=25-935) →
   *United States v. Kevin LaMarcus Mitchell*, docket id 73280976.
8. `call_endpoint` (docket-entries, docket=73280976) → 0 results (RECAP-only endpoint; no SCOTUS entries).
9. `get_endpoint_item` (opinions, 11344434, fields=plain_text) → full *Hemani*
   opinion text; grepped locally for the disposition. Key passages:
   "The judgment of the Fifth Circuit is affirmed." and "We do not address
   18 U.S.C. §922(g)(1)'s provision disarming individuals convicted of
   felonies (often including drug-related ones)."

## Web fetches (all failed — no content used)

10. `https://www.supremecourt.gov/RSS/Cases/JSON/25-935.json` → HTTP 403.
11. `https://www.supremecourt.gov/RSS/Cases/JSON/25-1001.json` → HTTP 403.
12. `https://www.courtlistener.com/opinion/10876933/united-states-v-hemani/` → empty page content.
13. `https://www.courtlistener.com/docket/73280976/docket/` → HTTP 403.

## Corpus (`fedcourts query`, service backend)

14. `uv run fedcourts query --court scotus --era modern --limit 8` → 0 rows
    (invalid era label; eras are decades like `2020s`).
    stderr: `ranged corpus reads: 429 GET(s), 112328704 byte(s)`
15. `uv run fedcourts query --court scotus --limit 3` → sample rows to learn
    the row shape (`date_cert_denied`, `docket_number`, ...).
    stderr: `ranged corpus reads: 428 GET(s), 112066560 byte(s)`
16. `uv run fedcourts query --court scotus --era 2020s --include-open --limit 2000`
    → request validation error (limit ≤ 500); no transfer line.
17. `uv run fedcourts query --court scotus --era 2020s --include-open --limit 500`
    → corpus service timeout; no transfer line.
18. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 300`
    → found the companion government petitions:
    *United States v. Kevin LaMarcus Mitchell*, No. 25-935, **cert denied
    2026-06-29**; *United States v. Edward Cockerham*, No. 25-1029, **cert
    denied 2026-06-08**. (*Doucet*, No. 25-1001, not among the 300 ranked
    rows; its Apr. 27, 2026 denial rests on the BIO's citation only.)
    stderr: `ranged corpus reads: 178 GET(s), 46661632 byte(s)`

## Base rates

- Committed `metrics/statpack.md`: "Modern discretionary-cert petitions by
  disposition", originating-circuit (ca5), relist-count, CVSG, and per-Term
  tables. (No salience-band section in the committed statpack version.)
