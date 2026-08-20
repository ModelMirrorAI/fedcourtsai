# Retrieval log

Beyond the provisioned inputs (snapshot 2026-01-13, questions-presented.txt,
petition.txt, brief-in-opposition.txt, documents.json, event.yaml,
record/context.json) and the committed `metrics/statpack.md`:

## Corpus

- `uv run fedcourts query --court scotus --disposition dismissed --limit 5`
  — shape of recent Rule 46 / dismissed cert dockets.
  stderr: `ranged corpus reads: 40 GET(s), 10485760 byte(s)`
- `uv run fedcourts corpus-info` (and `--corpus-backend ranged`) — **failed**:
  the ranged backend needs the corpus remote URL, which the cell does not
  hold; blob-wide vintage unavailable, so vintage is stated from the query
  rows' `last_live_polled` (2026-08-03).

## CourtListener MCP

- `call_endpoint docket-entries` (docket=73275236) — 0 results (no RECAP
  entries for this SCOTUS docket).
- `get_endpoint_item dockets` (73275236) — docket metadata; `date_terminated:
  null`.

## Web

- WebSearch: `"25-293" "General Dynamics" Scharpf Supreme Court solicitor
  general brief` — SCOTUSblog case page, Chamber case page, HR Dive CVSG
  coverage; confirmed CVSG outstanding, no disposition reported.
- WebSearch: `"General Dynamics" Scharpf no-poach shipbuilders settlement 2026
  abeyance Supreme Court` — Law360: "General Dynamics Seeks Pause In No-Poach
  High Court Bid"; plaintiffs dismissed GD from the suit and settled with
  remaining defendants.
- WebFetch: `https://www.supremecourt.gov/docket/docketfiles/html/public/25-293.html`
  — **HTTP 403**, could not read the authoritative post-January docket.
- WebFetch: `https://www.scotusblog.com/cases/general-dynamics-corp-v-scharpf/`
  — timeline shows "Hold Petition in Abeyance" motion submitted May 18, 2026.
- WebFetch: `https://www.cohenmilstein.com/case-study/scharpf-et-al-v-general-dynamics-corp-et-al/`
  — Faststream settled Sept 16, 2025; Huntington Ingalls / Marinette Marine /
  Serco affiliate settlements Mar 19, 2026.
