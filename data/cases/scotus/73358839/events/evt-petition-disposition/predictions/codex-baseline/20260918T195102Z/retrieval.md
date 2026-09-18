# Retrieval record

- Read the provisioned event definition, September 18, 2026 snapshot, context, document manifest, questions presented, and petition sections identified in `reasoning.md`.
- Read the prediction contract and output schemas; inspected local path and serialization helpers for contract-compliant output. These are tooling references, not additional case evidence.
- Read committed `metrics/statpack.md`: modern discretionary-cert dispositions, circuit cut, paid-segment relist and CVSG cuts, and sal-v4 band table. Used only displayed Terms 2017–2024 for the numerical band anchor; excluded 2025 and 2026. A local calculation pooled the rounded reached-elevated percentages over n=2,810, yielding approximately 0.172379.
- Ran `git log -1 --format='%cs %h' -- metrics/statpack.md`, returning September 14, 2026 and `55121cdb8`. This dates the committed artifact, not the underlying corpus's last pull.
- Attempted `web.run` search for `site.supremecourt.gov rules Rule 11 certiorari before judgment imperative public importance`. The tool returned no usable content or source references.
- Attempted `web.run` open of the Supreme Court's 2023 Rules PDF at the official filing-and-rules path. The tool again returned no usable content. No web-derived factual assertion was used, and no case-specific web search was made.
- Ran `uv run fedcourts paths --court scotus --docket 73358839 --event evt-petition-disposition --role predictor`. The first attempt failed because the default uv cache was read-only; retrying with a temporary writable cache succeeded. This resolves local paths, not corpus evidence.
- No `fedcourts query`, `open-events`, CourtListener MCP lookup, live docket retrieval, or outcome-file read occurred. Accordingly there is no ranged-corpus transfer line to report.
