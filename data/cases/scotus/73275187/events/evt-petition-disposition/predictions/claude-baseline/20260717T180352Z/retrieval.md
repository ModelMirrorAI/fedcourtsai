# Retrieval log — scotus/73275187 / evt-petition-disposition / claude-baseline / 20260717T180352Z

Beyond the provisioned inputs (snapshot `2026-07-17.json`, `questions-presented.txt`,
`petition.txt`, `brief-in-opposition.txt`, `documents.json`), this cell consulted:

## Corpus tooling

- `uv run fedcourts query --court scotus --citation "586 U.S. 146" --limit 3`
  — **failed**: `corpus service at http://127.0.0.1:8377 is unreachable — is the
  sidecar running? (fedcourts corpus-serve): timed out`. No `ranged corpus
  reads:` line was printed (the query never reached the corpus). No further
  query attempts; fell back to the committed statpack.
- Read committed `metrics/statpack.md` (no transfer; a repo file): modern
  discretionary-cert disposition split, relist-count cut, CVSG cut, per-Term
  table. The salience-band table referenced in the prompt is not present in the
  committed statpack version.

## CourtListener MCP

- No MCP calls made. The provisioned snapshot (created 2026-07-13, current to
  the docket) plus supremecourt.gov filings covered the record; CourtListener
  adds little for a SCOTUS docket.

## Direct document fetch (case's own record, forward mode)

- `curl` of the petitioner's supplemental brief PDF listed in the snapshot's
  Jun 25 2026 docket entry:
  `https://www.supremecourt.gov/DocketPDF/25/25-246/414988/20260625114103616_Jouppi%20v.%20Alaska%20-%20Supplemental%20Brief.pdf`
  (text extracted locally with pypdf). This identified the *Pung v. Isabella
  County* hold and the petition's post-*Pung* posture. (A WebFetch of the same
  URL was blocked with HTTP 403 first; curl succeeded.)

## Web searches (forward mode, unrestricted)

- WebSearch: `Jouppi v. Alaska 25-246 Supreme Court cert petition relist
  excessive fines` — surfaced the SCOTUSblog case page, Alaska Beacon coverage
  (Sept. 2025, pre-snapshot), and the docket PDFs. No disposition surfaced.
- WebFetch: `https://www.scotusblog.com/cases/case-files/jouppi-v-alaska/` —
  confirmed the petition is still **pending** (no grant/denial), distributions
  9/29/2025, 12/12/2025, 6/29/2026. No outcome-revealing material encountered.

Total retrieval calls: 1 corpus query attempt (failed), 1 web search, 2 URL
fetch attempts (1 blocked, 1 succeeded), 1 web page fetch — well under budget.
