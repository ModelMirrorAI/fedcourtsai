# Retrieval Log

Consulted beyond the provisioned inputs:

- Base-rate context: `metrics/statpack.md` and `metrics/statpack.json`.
  - Used the SCOTUS resolved slice: 296 resolved rows, with 4 grants (about 1.4%), 13 denials, 47 dismissals, and 232 other dispositions.
  - The recent Term rows in `metrics/statpack.json` for Terms 2023, 2024, and 2025 had no resolved rows, so they did not provide a usable Term-specific grant rate.

- Corpus lookup attempted: `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --limit 10 --corpus-backend ranged`.
  - No `ranged corpus reads: ...` line printed. The command failed before returning priors because the runner could not resolve the remote corpus endpoint host.
  - Error category used for reasoning: remote corpus access unavailable; no priors were retrieved.

- Official Supreme Court PDF lookup attempted via browser tool using the petition PDF URL listed in `record/documents/documents.json`.
  - The browser tool returned no extractable petition text. The provisioned local `petition.txt` was also blank except for newlines.

- Web search attempted: `site:supremecourt.gov Andron Miguel Francis Allstate Insurance Company 25-1218 petition certiorari`.
  - No usable additional text or case-specific merits context surfaced.

- Official Supreme Court docket HTML URL attempted via browser tool for docket `25-1218`.
  - No usable additional content surfaced beyond the provisioned snapshot.

No CourtListener MCP lookup was available through this session's exposed tools.
