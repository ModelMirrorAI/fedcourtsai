# Retrieval record

## Provisioned materials

Read the event definition, case-level `record/context.json`, `record/snapshots/2026-09-15.json`, `record/documents/documents.json`, questions-presented text, and selected substantive portions of the petition and brief in opposition. No reply or amicus document text was retrieved. No outcome artifact, another predictor's output, or labeling-measurement artifact was read.

## Additional local material

- `metrics/statpack.md`: modern discretionary-cert disposition section, paid-segment relist/CVSG cuts, and the sal-v4 per-Term reached-band table. The anchor uses only displayed Terms 2017–2024. A heading search also surfaced other aggregate section headings and rows; none of the interim or merits rates informed this cert forecast.
- `metrics/statpack.json`: schema keys and Term/segment objects to inspect the same sal-v4 baseline reached rates. Local arithmetic pooled the prior-Term weighted denominators; this was not a live corpus query.
- Contract reads: `AGENTS.md`, `.github/prompts/predict.md`, and the prediction, agent-flags, and agent-tooling schemas.
- Path resolution: `uv run fedcourts paths --court scotus --docket 73281647 --event evt-petition-disposition --role predictor`. The first attempt failed because the default uv cache was read-only. Repeating with `UV_CACHE_DIR=/tmp/uv-cache` succeeded. No corpus prior lookup occurred and no ranged-corpus transfer line was emitted.

## External attempts

1. `web.run` search: `site.supremecourt.gov opinions 2024 Baker McKinney Sotomayor Gorsuch 23-1363`. No result content was returned to the agent.
2. `web.run` open attempt: `https://www.supremecourt.gov/opinions/24pdf/23-1363_d1o3.pdf`. This was an attempted earlier-case opinion locator, not a verified citation; no document content was returned or used.
3. CourtListener MCP `search`: `type="o"`, `case_name="Baker v. City of McKinney"`, `court="scotus"`, `filed_before="2025-01-01"`, `num_results=3`. Returned HTTP 429, 300/hour limit, expected availability in 895 seconds. No cases or snippets were returned. No retry or direct REST fallback was attempted.

No external request targeted Pena's disposition or subsequent history. No outcome-revealing material was encountered. All substantive case and authority descriptions used in the forecast come from the pre-decision provisioned materials, with the parties' disputed characterizations kept separate.
