# Retrieval record

## Supplied inputs and local reference material

- Read `AGENTS.md`, `.github/prompts/predict.md`, and the prediction/tooling schemas; consulted the path and serialization helpers to create contract-compliant artifacts.
- Ran `uv run fedcourts paths --court scotus --docket 73278555 --event evt-argument-judgment --role predictor`. The first attempt could not initialize the default read-only uv cache; rerunning with a writable cache succeeded. No outcome path was opened.
- Read this cell's `event.yaml`, case-level `context.json`, `record/snapshots/2026-10-07.json`, `documents.json`, `questions-presented.txt`, `argument-transcript.txt`, and `argument-features.json`.
- Read relevant sections of the provisioned petitioner and respondent merits briefs, petitioner's merits reply, and United States merits amicus brief. A read-only subagent reviewed these four briefs and independently checked the transcript for contrary evidence. It performed no external retrieval and wrote no files. The core passages used in the forecast were checked locally.
- Consulted the merits, per-Justice vote, and authorship sections of committed `metrics/statpack.md` / `metrics/statpack.json`; used only Terms strictly before grant Term 2025 for pooled references. Performed local arithmetic on those rows. Did not use cert-band rates or query the live corpus.

## General precedent retrieval

1. Web search queries: `site.supremecourt.gov opinions 2021 Hughes Northwestern 595 170 context specific inquiry` and `site.supremecourt.gov opinions Dudenhoeffer 573 409 425 prudence pleading`. The tool returned no usable visible content.
2. Web open attempt: official Supreme Court Hughes opinion PDF at `https://www.supremecourt.gov/opinions/21pdf/19-1401_m6io.pdf`. The tool returned no usable visible content; no opinion body was incorporated from that attempt.
3. CourtListener MCP `search`, type `o`, citation `595 U.S. 170`, one result requested, metadata fields requested. Returned Hughes v. Northwestern Univ., decided January 24, 2022, citation 595 U.S. 170, with the CourtListener case path `/opinion/6244621/hughes-v-northwestern-univ/`. This confirmed identity/citation only; it did not provide the opinion body.
4. CourtListener MCP `search` for the same citation requesting `caseName`, `opinions`, `cluster_id`, and `dateFiled` was rejected with HTTP 429. Stopped live legal retrieval rather than attempting a REST fallback. The forecast's substantive treatment of precedent rests on the provisioned briefs and argument.

There were no `fedcourts query` or `open-events` calls and therefore no ranged-corpus transfer lines. No retrieval sought this case's judgment, subsequent history, opinion, or decision coverage. No other cell's forecast or evaluation was consulted.
