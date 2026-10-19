# Retrieval record

- Read the provisioned event, context, October 19, 2026 snapshot, document manifest, questions presented, and relevant portions of petition, opposition, reply, and appendix. No outcome file, other prediction, or labeling-measurement artifact was consulted.
- Beyond those inputs, consulted committed `metrics/statpack.md`: modern discretionary-cert dispositions, paid-segment relist and CVSG cuts, and sal-v4 per-Term band table. Consulted `metrics/statpack.json` for exact baseline reached-rate numerators and denominators, pooling only displayed Terms 2017–2024. Calculation: sum(prefix_est_grant_rate * prefix_weighted_resolved) / sum(prefix_weighted_resolved) = 593 / 11580 = 0.0512089810. Did not use later-Term rates as the anchor.
- Ran `uv run fedcourts paths --court scotus --docket 73539054 --event evt-petition-disposition --role predictor`. Initial attempt failed because the default uv cache was read-only; retry with a writable temporary cache succeeded. This resolves paths and is not a corpus lookup.
- Web search attempted: `site.supremecourt.gov Rule 10 considerations governing review certiorari`. The tool returned no usable content.
- Web open attempted on the official Court rules PDF at `https://www.supremecourt.gov/filingandrules/2023RulesoftheCourt.pdf`, followed by a find for `Review on a writ`. Both returned no usable content. No case-specific search was made and no search result was incorporated.
- No CourtListener MCP lookup, `fedcourts query`, or `open-events` lookup was made. There are no ranged-corpus transfer lines to report.
