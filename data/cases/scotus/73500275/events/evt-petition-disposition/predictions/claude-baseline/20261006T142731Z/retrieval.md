# Retrieval log

Provisioned inputs read: `record/context.json`, `record/snapshots/2026-10-06.json`,
`record/documents/documents.json`, `questions-presented.txt`, `petition.txt` (QPs,
introduction, statement, argument parts I to IV), `brief-in-opposition.txt` (in full), and
the committed `metrics/statpack.md` (modern-cert section, circuit cut, relist and CVSG
cuts, per-Term salience-band table).

## Corpus lookups

- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 8`
  stderr: `ranged corpus reads: 28 GET(s), 7208960 byte(s)`
  Returned OT2025/OT2026 grants and substantive applications, none securities-related; no
  case-specific prior used. Run mainly to confirm the corpus service was reachable.
- Committed case tree (`git ls-files` / `event.yaml` reads, not a corpus query): located the
  Robinhood petition as `scotus/73280982` (events `evt-petition-disposition` and
  `evt-order-cvsg-disposition`, both unresolved, CVSG moment opened 2026-06-01). Read that
  cell's committed `retrieval.md` and grepped its `reasoning.md` for the SG-brief status as
  of 2026-09-18 (unconfirmed there too). No outcome file exists for it and none was read.

## CourtListener MCP lookups

- `search` type=d, court=scotus, docket_number=25-944: 0 results.
- `search` type=d, court=scotus, q="Robinhood Markets Sodha": 0 results.
- `call_endpoint` dockets, court=scotus, docket_number=25-944: **HTTP 429 rate limit**
  (1400/day exhausted; available again in about 62 minutes).
- `get_endpoint_item` dockets/73500275: **HTTP 429 rate limit**, same message.
  No REST fallback was attempted; degraded to the sources below per the prompt.

## Web

- `WebSearch`: "Robinhood Markets v. Sodha 25-944 Solicitor General brief certiorari".
  Surfaced the supremecourt.gov docket page, SCOTUSblog case page, the Robinhood BIO PDF,
  and commentary; confirmed the June 1, 2026 CVSG and the May 28, 2026 conference.
- `WebFetch` https://www.supremecourt.gov/docket/docketfiles/html/public/25-944.html:
  proceedings list; last entry June 1, 2026 (SG invited). No SG brief, no disposition.
- `WebFetch` https://www.supremecourt.gov/docket/docketfiles/html/public/25-1376.html
  (this case): seven entries, identical to the provisioned snapshot; nothing after the
  September 21, 2026 BIO. No disposition surfaced.
