# Retrieval record

## Local reference material and setup

Read the task contract, `AGENTS.md`, `schemas/prediction.schema.json`, `schemas/agent_tooling.schema.json`, and `schemas/agent_flags.schema.json`. Read the supplied cell event, context, dated snapshot, document manifest, questions presented, and selected petition and appended appellate-opinion sections. No other predictor's or evaluator's output, QP-labeling artifact, or realized-outcome file was read.

Read the committed `metrics/statpack.md` modern-cert, circuit, paid-segment relist/CVSG/amicus, and per-Term sal-v4 tables. Read the corresponding `metrics/statpack.json` Term and segment fields to pool the baseline reached risk sets over OT2017-OT2024. Arithmetic using unrounded fields: 607 / 11,599 = 0.05233209759462023. This is a calculation on the supplied pack, not a fresh corpus census or an assertion of current corpus completeness.

The first setup attempts were:

1. `uv run fedcourts paths --court scotus --docket 73377829 --event evt-order-call-for-response-disposition --role predictor` — failed before execution because the default uv cache was read-only.
2. `uv run fedcourts query --help` — same cache initialization failure; no corpus request occurred.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 73377829 --event evt-order-call-for-response-disposition --role predictor` — succeeded, resolving the case and event path. The outcome was labeled evaluator-only and was not opened.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` — succeeded. Re-read the options with `UV_CACHE_DIR=/tmp/uv-cache COLUMNS=160 uv run fedcourts query --help` to avoid narrow terminal wrapping. These were help calls, not corpus lookups.

## Corpus lookup

Command:

```text
UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition denied --era 2020s --decided-before 2025 --limit 3
```

Reported transfer:

```text
ranged corpus reads: 43 GET(s), 11272192 byte(s)
```

Returned three denied petitions: `scotus/72483668` (24-1185), `scotus/72483835` (24-1329), and `scotus/72483937` (24-229). No opinion bodies were requested. This denial-filtered sample is not a random sample, not a subject-matter match, and not used to estimate a rate. The Term filter permits those general priors' later decision dates; this forward cell has no replay clock. None is this petition or a provisioned companion, and no subsequent history of this petition was queried.

## Web attempts

Every web call returned an empty displayed tool payload: no readable search results, quoted text, citation identifiers, or disposition claim. No factual premise was adopted from these attempts.

1. A combined search for `site.supremecourt.gov Rule 10 writ certiorari erroneous factual findings misapplication properly stated rule` and `site.uscode.house.gov 2 USC 1434 judicial branch study recommendations`.
2. An attempt to open the official Supreme Court rules PDF at host `www.supremecourt.gov`, path `/filingandrules/2023RulesoftheCourt.pdf`.
3. A search for `Supreme Court Rule 10 certiorari factual findings`.
4. A search for `2 USC 1434 judicial branch study recommendations`.

These sought general authorities only, not this petition's disposition. No CourtListener MCP lookup was attempted. There was no retrieval of the Court's live docket for this case and no outcome-revealing material encountered.
