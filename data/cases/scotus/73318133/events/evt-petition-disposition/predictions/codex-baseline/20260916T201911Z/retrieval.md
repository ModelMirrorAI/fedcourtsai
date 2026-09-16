# Retrieval log

- Read committed `metrics/statpack.md`: modern discretionary-cert population, originating-circuit context, paid-segment relist and CVSG cuts, and the `sal-v4` reached-band table. The numerical anchor uses only Terms 2017-2024. Calculated the denominator-weighted mean of the displayed rounded baseline reached rates locally: approximately 5.12025%, denominator 11,580. No corpus query, opinion hydration, or transfer-statistics line was produced.
- Web search attempted: `site.supremecourt.gov Rule 10 considerations governing review certiorari erroneously asserted findings fact`. No usable result content was returned.
- Web open attempted on `https://www.supremecourt.gov/filingandrules/2023RulesoftheCourt.pdf`, then a find for `A petition for a writ of certiorari is rarely granted`. Neither supplied usable content; that PDF was not used as evidence.
- Successfully retrieved the general text of Supreme Court Rule 10 through Cornell LII with `curl -fsSL --max-time 30 https://www.law.cornell.edu/rules/supct/rule_10`, limiting displayed output to the certiorari considerations. Used only the rule's distinction between compelling review grounds and factual-error correction. No case-specific query or outcome search was made.
- Ran `uv run fedcourts paths --court scotus --docket 73318133 --event evt-petition-disposition --role predictor`; the initial cache-path error was resolved by placing the cache in temporary storage. This was path resolution, not corpus retrieval.
- No CourtListener MCP calls; no other case records, opinions, or predictor outputs consulted.
