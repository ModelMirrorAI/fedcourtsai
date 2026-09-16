# Retrieval record

## Local reference material

- Read `AGENTS.md`, `.github/prompts/predict.md`, `schemas/prediction.schema.json`, `schemas/agent_tooling.schema.json`, and `schemas/agent_flags.schema.json` for the cell contract.
- Read the provisioned event, September 15, 2026 snapshot, context, document manifest, QP text, and selected substantive sections of both filed briefs. No other predictor's output or realized outcome was read.
- Read `metrics/statpack.md` modern discretionary-cert, circuit, paid-segment relist/CVSG, and sal-v4 segment tables; queried `metrics/statpack.json` locally with jq for the unrounded 2017–2024 baseline reached-rate calculation. Aggregate context only; no case-membership labeling artifacts were read.
- Ran `uv run fedcourts paths --court scotus --docket 73281642 --event evt-petition-disposition --role predictor`. The default cache path was read-only; repeating with the cache redirected to `/tmp/uv-cache` succeeded. This resolves paths, not corpus facts.
- No `fedcourts query`, `open-events`, or other live corpus lookup was used. No ranged-corpus transfer line was emitted.

## Web attempts

1. Search: `site.supremecourt.gov "Baker" "23-1363" "SOTOMAYOR"`. No usable output returned.
2. Search: `site.supremecourt.gov/opinions/24pdf "BAKER" "MCKINNEY"`. No usable output returned.
3. Attempted open: `https://www.supremecourt.gov/opinions/24pdf/23-1363_d1o3.pdf`. No usable output returned; neither the address nor opinion content was verified. No proposition relies on that attempted address.

## CourtListener MCP

- `search(type="o", case_name="Baker v. City of McKinney", court="scotus", filed_before="2024-12-01", num_results=3)` returned HTTP 429, reporting a 300/hour limit and availability in 864 seconds. No cases or opinion text were returned. No retry or REST fallback was attempted.

The historical Baker lookup was for precedent context, not Hadley's own outcome. All external attempts yielded no substantive content. No target-case disposition or subsequent-history search was made, and no outcome material was encountered.
