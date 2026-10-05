# Retrieval record

## Provisioned inputs

- Read `event.yaml`, `record/context.json`, and `record/snapshots/2026-10-05.json` for this case and event.
- Read the document manifest and questions presented; examined the petition and brief in opposition, including their introductions, descriptions of the appellate ruling, conflict arguments, and vehicle discussions. No other case filing was fetched.

## Committed statistical context

- Consulted `metrics/statpack.md`: modern discretionary-cert dispositions, originating-circuit cut, paid-segment relist and CVSG cuts, and sal-v4 prior-Term reached-band table.
- Consulted `metrics/statpack.json` for exact high-band reached rates and weighted denominators for Terms 2017–2025. Summed rate times denominator to 343 and denominators to 966, yielding 0.35507246376811596. No Term 2026 outcomes entered that pool.
- Ran `git log -1 --format='%h %cI' -- metrics/statpack.md metrics/statpack.json` to identify the committed artifact's vintage: `808f812e9`, September 28, 2026 at 12:02:50 UTC. This is not a corpus pull timestamp.

## External retrieval attempts

1. `web.run` search query: `site.supremecourt.gov Rule 10 considerations governing review certiorari conflict important federal question`. No visible search results or source content were returned.
2. `web.run` open of `https://www.supremecourt.gov/filingandrules/rules_guidance.aspx`. No visible page content was returned.
3. Repeated the same rules-page open once. Again no visible page content was returned.

These were general procedural-context attempts, not searches for this case. No externally retrieved proposition entered the prediction and no outcome-revealing material was surfaced.

## Corpus and CourtListener

No `fedcourts query` or `open-events` command and no CourtListener MCP lookup was made. There are therefore no ranged-corpus-read transfer lines to report.

The local path-resolution command was `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000130 --event evt-petition-disposition --role predictor`. The initial attempt without the writable cache override failed before execution because the default cache location was read-only. Path resolution retrieved no case facts or outcomes.
