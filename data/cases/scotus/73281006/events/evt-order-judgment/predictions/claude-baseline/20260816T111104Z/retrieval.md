# Retrieval log

Beyond the provisioned inputs (snapshot, BIO text, `documents.json`,
`context.json`, `event.yaml`) and the committed `metrics/statpack.md`:

## Corpus tooling

- `uv run fedcourts query --court scotus --era roberts "…"` — usage error
  (free-text positional args are not accepted); no read performed.
- `uv run fedcourts query --court scotus --citation "588 U.S. 180"` — no
  matching rows; stderr: `ranged corpus reads: 1329 GET(s), 348389376 byte(s)`
  plus a `note:` that the citation column holds a case's own reporter cites
  (161 of 590339 scotus rows carry citation data), so this was the wrong
  filter for a cases-citing-Knick lookup. Not retried, per the
  don't-burn-turns-on-sparse-filters guidance.

## CourtListener MCP

- `search` (opinions, ca6, `Grand "University Heights"`) — found the published
  Sixth Circuit opinion, cluster 10735939, decided 2025-11-13, docket 24-3876.
- `read_document` (opinion_id 10735939) — wrong document (the cluster id is
  not an opinion id; returned an unrelated Court of Federal Claims decision).
  Discarded.
- `get_endpoint_item` (clusters/10735939) — resolved sub-opinion 11202524;
  panel Sutton, Batchelder, Larsen.
- `read_document` (opinion_id 11202524, chunks 0–2 of 6) — the Sixth
  Circuit's ripeness analysis (Williamson County finality, Grace Community
  Church, responses to the cease-and-desist / futility / due process
  arguments).

## Web

- WebFetch `https://www.supremecourt.gov/qp/25-00965qp.pdf` — HTTP 403; the
  Court's QP PDF could not be fetched directly.
- WebSearch `Supreme Court cert granted "Grand v. City of University Heights"
  question presented` — grant coverage only (SCOTUSblog case page, ADF, ACLJ,
  local Cleveland outlets). No disposition surfaced; the case is pending.
- WebFetch `https://www.scotusblog.com/cases/grand-v-city-of-university-heights/`
  — verbatim question presented; grant date June 30, 2026; argument not yet
  scheduled.

All retrieval was forward-mode (pending case, unrestricted); nothing
outcome-revealing exists to surface.
