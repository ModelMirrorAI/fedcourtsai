# Retrieval log

## Local inputs and reference material

- Read `AGENTS.md`, `.github/prompts/predict.md`, and the prediction, agent-flags, and agent-tooling schemas.
- Read this cell's event definition, case-level context, September 16, 2026 snapshot, document manifest, questions presented, and relevant portions of the petition and opposition. No outcome, other predictor's output, or labeling artifact was read.
- Ran `uv run fedcourts paths --court scotus --docket 73318742 --event evt-petition-disposition --role predictor`. The initial attempt failed because the default uv cache location was read-only. Retried successfully with `UV_CACHE_DIR=/tmp/uv-cache`.
- Read `metrics/statpack.md`: modern-cert dispositions, originating circuit, paid-segment relist and CVSG cuts, and sal-v4 per-Term reached-band table. Used a local Python calculation to pool only Terms 2017–2024 from the displayed baseline cells: approximately 0.0512025 with weighted denominator 11,580. Inspected the top-level keys of `metrics/statpack.json`; no case-level corpus query was made.
- No `fedcourts query` or `open-events` call; no ranged corpus transfer line was emitted.

## General-law web attempts

1. `web.run` search queries: `site.supremecourt.gov Mireles Waco 502 U.S. 9 judicial immunity` and `site.supremecourt.gov Williams Pennsylvania 2016 579 U.S. 1 opinion`. The tool returned no usable content.
2. `web.run` open attempt for `https://www.govinfo.gov/content/pkg/USREPORTS-502/pdf/USREPORTS-502-9.pdf`. The tool returned no usable content.

Neither request named the target litigation or sought its outcome.

## CourtListener MCP

1. `search(type="o", citation="502 U.S. 9", num_results=1)` returned an unrelated Glaxo district-court result. Discarded as irrelevant; no follow-up read.
2. `search(type="o", case_name="Mireles v. Waco", court="scotus", num_results=1)` located the Supreme Court's October 21, 1991 opinion, cluster 112655, lead opinion 9432415.
3. `read_document(opinion_id=9432415)` supplied the primary majority opinion in Mireles, 502 U.S. 9. Used its general distinction between judicial acts, nonjudicial acts, and acts in the absence of jurisdiction.
4. `search_document(opinion_id=9432415, query="two sets", snippet_size=1100)` retrieved the central immunity-exception paragraph to ensure it was visible despite truncation in the full-document tool display.

No target-case live docket, subsequent history, or disposition was requested or surfaced. Historical outcomes in the general precedent were used only as general legal context.
