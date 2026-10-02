# Retrieval log

- Read the committed `metrics/statpack.md`, particularly its interim-application section and per-Term rows. Computed the strictly-prior 2016–2025 pool as 31 grants among 296 resolved substantive applications. No corpus query or opinion-body hydration was performed.
- Web search attempted: `site.supremecourt.gov Hollingsworth Perry 558 183 190 stay reasonable probability fair prospect irreparable harm`. The tool returned no usable content or source references.
- Web open attempted for the historical general-standard opinion at `https://www.supremecourt.gov/opinions/09pdf/09a648.pdf`. The tool returned no usable content. Neither web call concerned Wagner or sought this cell's outcome; neither informed the forecast.
- Ran `uv run fedcourts paths --court scotus --docket 9526000446 --event evt-motion-disposition --role predictor`. The first invocation failed because the default uv cache was read-only; retrying with a temporary writable cache succeeded. This resolved paths only, not corpus records.
- Read the prediction, tooling, and flags schemas and the repository serialization helper for output compliance. No CourtListener MCP lookup, `fedcourts query`, or `open-events` call was made; there are no ranged-corpus transfer lines to report.

No case-specific external retrieval was used. The case evidence consists of the provisioned event, snapshot, context, and application text and manifest.
