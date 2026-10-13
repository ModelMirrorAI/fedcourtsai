# Retrieval record

## Provisioned inputs

Read event.yaml, record/context.json, record/snapshots/2026-10-13.json, and record/documents/documents.json. Consulted the petition's questions presented, introduction, substantive asylum discussion, and certworthiness section; the opposition's introduction, asylum/vehicle discussion, and importance discussion; and the reply's substantive and review sections, including its companion-case discussion on page 12. Reads were selective, not a representation that every appendix page was inspected.

## Additional local context

- Read AGENTS.md, .github/prompts/predict.md, and the prediction/tooling/flags schemas for the contract.
- Read metrics/statpack.md: modern-cert disposition and circuit cuts, paid-segment relist/CVSG cuts, and sal-v4 segment table. Inspected metrics/statpack.json structure and computed the federal reached-rate pool for displayed Terms 2017–2025: 143/203 = 0.7044334975. Excluded 2026 from the anchor.
- Ran `git log -1 --format='%h %cI' -- metrics/statpack.md` to identify the committed pack version: ea0a1e70a, October 12, 2026 at 21:45:55 UTC. No live corpus freshness check was performed.
- Ran `uv run fedcourts paths --court scotus --docket 9026000239 --event evt-petition-disposition --role predictor`; the first attempt failed because the default cache directory was read-only. Retried successfully with a writable temporary cache. This was path resolution, not a corpus lookup.
- Consulted fedcourtsai.paths and fedcourtsai.serialize for output layout and serialization conventions.

No `fedcourts query` or `open-events` lookup was made, so there is no ranged-corpus transfer line. No CourtListener MCP lookup was made. No outcome file, other predictor output, or labeling-measurement artifact was read.

## Attempted general web context

The web tool was called for a general official-source query, `site.supremecourt.gov rules Rule 10 important question federal law certiorari`, followed by attempts to open the Supreme Court's 2023 Rules PDF and rules/guidance page. All three calls returned no visible source content. They supplied no evidence and were not relied on. No query named this petition or sought its disposition, subsequent history, or decision coverage.
