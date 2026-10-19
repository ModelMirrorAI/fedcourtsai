# Retrieval record

## Committed aggregate context

- Read the modern discretionary-cert, originating-circuit, paid-segment relist/CVSG, per-Term, and sal-v4 segment sections of `metrics/statpack.md`.
- Read structural fields and the relevant segment fields in `metrics/statpack.json`. A local Python calculation pooled the reached-baseline fields for Terms 2017-2025: 643 / 12,877 = 0.04993399083637493. The current Term was not included in the anchor.
- Ran `git log -1 --format='%h %cI' -- metrics/statpack.md metrics/statpack.json` to identify the committed artifact vintage: `cf9ae960e 2026-10-13T19:17:46Z`. This does not establish the remote corpus's freshness.
- No `fedcourts query` or `open-events` lookup was made. There is therefore no ranged-corpus-read transfer line. No CourtListener MCP lookup was made.

## General web lookup attempts

These requests were confined to general legal context, not this petition or its disposition. The tool returned no usable content to this session; no external result supplied a forecast fact.

1. Search queries: `site.supremecourt.gov opinions 2022 Groff DeJoy 22-174 undue hardship` and `site.supremecourt.gov Rule 10 writ certiorari erroneous factual findings misapplication properly stated rule`.
2. Open attempt: `https://www.supremecourt.gov/opinions/22pdf/22-174_k536.pdf`.
3. Open attempt: `https://www.supremecourt.gov/filingandrules/2026RulesoftheCourt.pdf`.
4. Search queries: `site.supremecourt.gov "22-174_k536.pdf"` and `site.supremecourt.gov "Rule 10" "erroneous factual findings"`.
5. Repeated open attempt: `https://www.supremecourt.gov/opinions/22pdf/22-174_k536.pdf`.
6. Find attempt for `erroneous factual` in `https://www.supremecourt.gov/filingandrules/2023RulesoftheCourt.pdf`.

## Local contract checks

Read `AGENTS.md`, `.github/prompts/predict.md`, the relevant output schema fields, and the path/serialization helpers. Resolved the output location with `fedcourts paths` and `CasePaths`. The first CLI invocation encountered a read-only default cache; rerunning with a writable temporary cache succeeded. These operations supplied no additional case evidence. No outcome files, other predictor outputs, or topic-labeling artifacts were consulted.
