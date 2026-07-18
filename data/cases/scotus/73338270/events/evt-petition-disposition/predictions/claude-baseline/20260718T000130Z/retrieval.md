# Retrieval log — scotus/73338270 / evt-petition-disposition / claude-baseline / 20260718T000130Z

Provisioned inputs read: `record/snapshots/2026-07-17.json`,
`record/documents/questions-presented.txt`, `record/documents/petition.txt`,
`record/documents/documents.json`, `record/context.json` (mode: `forward`),
the event definition, and the committed `metrics/statpack.md` (modern-cert
disposition, originating-circuit, relist, CVSG, and per-Term tables).

## Corpus lookups (`fedcourts` CLI)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   — stderr: `ranged corpus reads: 149 GET(s), 39059456 byte(s)`.
   Grounding sample of recent granted SCOTUS priors; no vaccine-mandate
   matches surfaced (the query surface is filter-based, no free-text search).

## CourtListener MCP

1. `search` (type=d, court=scotus, docket_number=25-1119) — **failed with
   HTTP 429** (`Rate limit exceeded: 1200/day`). The sidecar's daily quota was
   already exhausted at this cell's first call; per the contract I degraded to
   the corpus tooling and public web sources below and made no further MCP
   calls.

## Web retrieval (forward mode, unrestricted)

1. WebSearch: `Curtis v. Inslee Supreme Court 25-1119 certiorari petition status`
   — surfaced the June 1, 2026 order list PDF.
2. WebSearch: `Health Freedom Defense Fund v. Carvalho Supreme Court 25-765 cert petition`
   — case background; extension history.
3. WebSearch: `"25-1119" Curtis Inslee "response" requested OR distributed conference 2026`
   — no additional signal.
4. WebSearch: `"25-765" Health Freedom Defense Fund Carvalho certiorari denied OR granted OR distributed 2026`
   — surfaced the May 18, 2026 order list PDF. (The search engine's summary
   claimed 25-765 was *granted*; direct inspection of the PDF showed this was
   wrong — it appears under CERTIORARI DENIED.)
5. WebFetch: `https://www.supremecourt.gov/docket/docketfiles/html/public/25-1119.html`
   — HTTP 403 (blocked); fell back to order-list PDFs.
6. Direct download + text extraction:
   `https://www.supremecourt.gov/orders/courtorders/060126zor_k53l.pdf`
   (June 1, 2026 order list) — 25-1119 Curtis, 25-1055 Sweeney, and 25-1203
   Horsley all under CERTIORARI DENIED; the order list's dissents are
   unrelated cases.
7. Direct download + text extraction:
   `https://www.supremecourt.gov/orders/courtorders/051826zor_h315.pdf`
   (May 18, 2026 order list) — 25-765 Health Freedom Defense Fund v. Carvalho
   under CERTIORARI DENIED, no recorded dissent.

No lookup touched this case's own disposition (it is pending; the response is
due August 31, 2026). The companion-petition denials predate the snapshot and
are disclosed as decisive forward signal in `flags.json`.
