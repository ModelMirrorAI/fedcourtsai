# Retrieval record

- Read `metrics/statpack.md`: modern discretionary cert, paid-segment relist and CVSG cuts, and the sal-v4 reached-band table.
- Read the corresponding Term segment fields in `metrics/statpack.json`; pooled elevated reached counts over the displayed eligible Terms 2017-2025 with `jq`: 521 / 3,085 = 0.1688816856. Inspected its top-level keys and the Term 2026 aggregate structure to identify the fields; excluded that Term from the anchor.
- Ran `git log -1 --format='%h %cI' -- metrics/statpack.json` for artifact vintage: `808f812e9`, September 28, 2026 at 12:02:50 UTC. This does not establish corpus-wide freshness.
- Web search attempted: `site.ca6.uscourts.gov "Mikel" "Quin" "2023"`.
- Web search attempted: `site.loc.gov "Smith v. Organization of Foster Families" "431"`.
- Web search attempted: `"Mikel v. Quin" "58 F.4th"`.
- Web search attempted: `Supreme Court Rule 10 certiorari considerations governing review`.
- Official rules PDF open attempted: `https://www.supremecourt.gov/filingandrules/2023RulesoftheCourt.pdf`.
- All three web tool calls returned no usable content. No web-derived fact informed the forecast, and no search sought this case's outcome.
- No `fedcourts query` or `open-events` calls; no ranged corpus reads line; no CourtListener MCP lookup.

Local contract/schema reads, the path-resolution command, inspection of path/serialization helpers, and output validation were tooling operations, not additional case evidence. The first path-resolution attempt failed because the default package cache was read-only; using a writable temporary cache succeeded.
