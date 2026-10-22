# Retrieval record

- Read the committed `metrics/statpack.md`: modern-cert disposition, originating-court context, paid-segment relist and CVSG cuts, per-Term table, and sal-v4 reached-band table. Read `metrics/statpack.json` for matching exact Term 2017–2025 baseline reached denominators and rates. A local `jq` aggregation returned 644 grant-family outcomes / 12,883 weighted resolved = 0.04998835674920438. This was committed-pack arithmetic, not a live corpus query.
- Ran `uv run fedcourts corpus-info --help`, then `uv run fedcourts corpus-info` with a writable temporary cache. The latter failed: the service backend has no client-side connection and only query/open-events forward to the service. No corpus vintage or case rows were returned; no ranged-corpus transfer line was printed.
- Web search attempt: `site.supremecourt.gov Rule 10 considerations governing review writ certiorari error correction`. The tool returned no usable content or source identifiers.
- Web open attempt: `https://www.law.cornell.edu/rules/supct/rule_10`. The tool returned no usable content or source identifiers. No external legal proposition was taken from these attempts.
- No CourtListener MCP lookup, `fedcourts query`, or `open-events` lookup was made. No request sought this case's outcome, subsequent history, or post-decision coverage.

Local contract, schema, path-resolution, and validation commands are administrative checks, not additional case evidence. The first path-resolution attempt encountered an unwritable default cache; repeating it with a temporary cache succeeded.
