# Retrieval record

## Provisioned inputs

Read the specified event YAML, case-level `record/context.json`, `record/snapshots/2026-10-04.json`, and `record/documents/documents.json`, `questions-presented.txt`, and `petition.txt`. No outcome file, other predictor output, or topic-label measurement artifact was read.

## Beyond the provisioned inputs

- Read the committed `metrics/statpack.md`: modern-cert dispositions, originating-court cuts, paid-segment relist and CVSG cuts, and the sal-v4 per-Term segment table. Read matching aggregate fields in `metrics/statpack.json`. Pooled the baseline reached rates over every displayed prior Term, 2017–2025, with `jq`: 638 / 12720 = 0.05015723270440252.
- Ran `git log -1 --format=%cI -- metrics/statpack.json` for artifact vintage: `2026-09-28T12:02:50Z`. This is not a corpus refresh timestamp.
- Attempted one web search: `site.supremecourt.gov rules Rule 10 rarely granted erroneous factual findings misapplication properly stated rule law`. The web tool returned no content or source identifiers.
- Attempted to open the official Supreme Court rules-guidance page twice (`https://www.supremecourt.gov/filingandrules/rules_guidance.aspx`). Both calls returned no content or source identifiers. No legal proposition was taken from these attempts, and no case-specific search was made.
- No CourtListener MCP call, corpus query, or open-events lookup was made. Consequently there are no ranged-corpus transfer lines to report.

## Local contract and tooling reads

Read `AGENTS.md`, the prediction prompt, and the prediction, tooling, and flags schemas. Ran `uv run fedcourts paths --court scotus --docket 9026000066 --event evt-petition-disposition --role predictor`; the default cache location was read-only. Retried successfully with `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts paths --court scotus --docket 9026000066 --event evt-petition-disposition --role predictor`. Path resolution is not case-fact retrieval.
