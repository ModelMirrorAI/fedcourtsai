# Retrieval log

## Committed aggregate context

- Read `metrics/statpack.md`: modern discretionary-cert dispositions, originating circuit, paid scored-segment relist and CVSG cuts, and the sal-v4 per-Term reached-band table.
- Read `metrics/statpack.json` for the corresponding unrounded strictly prior baseline risk-set counts. Pooled displayed Terms 2017–2024 only: 593 grant-equivalents / 11,580 weighted resolved petitions. Local `jq` performed the calculation; no corpus query or remote corpus reads were used.
- Pack identification: SHA-256 of `metrics/statpack.json` is `640587577b05402aec23f24492d4b9bc0097431bcd817d66c6b2a2218296c061`. No current corpus-wide pull/snapshot vintage was queried; this is the committed aggregate artifact, not a live census.

## General legal standard only

- Web search attempted: `site.supremecourt.gov rules Rule 10 considerations governing review certiorari erroneous factual findings`. No visible result was returned.
- Two web opens attempted for `https://www.supremecourt.gov/filingandrules/rules_guidance.aspx`. Neither returned visible content.
- Shell `curl` retrieved that official rules-guidance page, identifying the rules effective March 16, 2026 at `https://www.supremecourt.gov/filingandrules/2026RulesoftheCourt_WEB.pdf`.
- A `curl`/`pdftotext` extraction attempt failed because `pdftotext` was unavailable. Two in-memory Python `urllib.request`/`pypdf` fetches then extracted Rule 10's text on printed pp. 5–6. No PDF file was saved. Only the general certiorari standard informed the forecast.

No CourtListener MCP lookup, `fedcourts query`, or `open-events` call was made; there are no ranged-corpus-read transfer lines to report. No external search concerned this petition or its disposition.

## Local tooling

Resolved the event with `uv run fedcourts paths --court scotus --docket 73389313 --event evt-petition-disposition --role predictor`. The first attempt failed on the default read-only uv cache; retrying with a temporary writable cache succeeded. Schema/serialization checks and `uv run fedcourts validate data` are local validation, not predictive retrieval.
