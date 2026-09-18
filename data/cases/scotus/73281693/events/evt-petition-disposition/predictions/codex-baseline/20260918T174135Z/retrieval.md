# Retrieval record

## Provisioned inputs

- Read `event.yaml`, `record/context.json`, and `record/snapshots/2026-09-17.json` for this cell; inspected snapshot fields and the complete proceedings list.
- Read `record/documents/documents.json`, `questions-presented.txt`, and substantive excerpts from `petition.txt` and `brief-in-opposition.txt`, focusing on the claimed split, the competing readings of the decision below, and vehicle objections. The reply appears in the snapshot but its text was not retrieved.

## Context beyond provisioned inputs

- Read `metrics/statpack.md`: modern discretionary-cert disposition/circuit cuts, paid-segment relist and CVSG cuts, and the sal-v4 segment-by-Term table. Inspected `metrics/statpack.json` and computed the elevated reached-rate pool for the displayed Terms 2017–2024: 484 / 2810 = 0.17224199288256228. No own-Term or later-Term rate was used as an anchor.
- Ran `git log -1 --format='%h %cI' -- metrics/statpack.md` to identify committed artifact vintage: `55121cdb8 2026-09-14T11:02:00Z`. This was not a live corpus freshness check.
- Web search: `site.supremecourt.gov opinions 2022 Groff DeJoy 22-174 substantial increased costs`. The tool returned no usable results.
- Attempted web open of the official general-precedent opinion at `https://www.supremecourt.gov/opinions/22pdf/22-174_k536.pdf`. The tool returned no usable content. No external opinion text informed the forecast; the treatment of Groff rests on the provisioned briefs.
- No CourtListener MCP calls, corpus `query` calls, or `open-events` calls. Accordingly there are no ranged-corpus transfer lines to report. No retrieval sought this petition's disposition, subsequent history, or current docket.

## Contract and tooling reads

Read `AGENTS.md`, `.github/prompts/predict.md`, prediction/tooling schemas, and relevant path/serialization helper definitions. Ran `fedcourts paths --court scotus --docket 73281693 --event evt-petition-disposition --role predictor` through `uv run`. The first attempt failed because the default uv cache was read-only; retrying with a temporary cache succeeded. Validation is performed with `uv run fedcourts validate data` using the same cache override. These are contract/tooling operations, not additional case retrievals.
