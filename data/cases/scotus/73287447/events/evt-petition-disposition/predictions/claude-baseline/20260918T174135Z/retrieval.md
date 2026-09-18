# Retrieval log

Beyond the provisioned inputs (snapshot `2026-09-17.json`, `context.json`, `questions-presented.txt`, `petition.txt`, `brief-in-opposition.txt`) and the committed `metrics/statpack.md`:

## Corpus (`fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 6`
   stderr: `ranged corpus reads: 23 GET(s), 6029312 byte(s)`
   Returned recent granted SCOTUS rows (mostly emergency applications and two OT2025 cert grants); not doctrinally comparable, not used for the number.
2. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 4`
   stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm cache)
   Same character; not used for the number.
   (An initial attempt with a `--text` flag was rejected by the CLI, which takes no free-text argument.)

## CourtListener MCP

3. `call_endpoint docket-entries` for docket 73287447, ordered by date — 0 results (SCOTUS dockets carry no RECAP entries).
4. `search type=d court=scotus docket_number=25-1388` (United Biologics v. Amerigroup, cited in the BIO) — 0 results.
5. `get_endpoint_item dockets 73287447` — confirmed case name, docket number 25-1243, filed 2026-05-01, `date_terminated: null`, last modified 2026-09-09.
6. `search type=d court=scotus case_name="United Biologics"` — 0 results.

## Web

7. WebSearch: `Nexstar v. DirecTV Supreme Court certiorari petition antitrust standing nonpurchaser 25-1243` — trade-press coverage of the petition (May 2026) and the BIO (Aug 2026) from thedesk.net, Communications Daily and RBR; a justice.gov link to the DOJ amicus brief below. No disposition.
8. WebFetch: `https://www.justice.gov/atr/media/1361556/dl` — returned raw PDF bytes; text extracted locally with `pdftotext`. It is the Brief for the United States as amicus curiae in support of neither party, DirecTV v. Nexstar, 2d Cir. No. 24-981, filed July 24, 2024, signed by AAG Jonathan S. Kanter et al.; it argues the district court misunderstood the harms from price fixing in its antitrust-standing analysis.
9. WebSearch: `"United Biologics" Amerigroup Supreme Court petition 25-1388 certiorari` — petition filed June 12, 2026 from the Sixth Circuit; an indirect-purchaser (Illinois Brick) case, not a non-purchaser standing case.

Total: 2 corpus queries, 4 MCP calls, 2 web searches, 1 web fetch.
