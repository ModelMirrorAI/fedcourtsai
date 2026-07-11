# Retrieval

## Corpus and base-rate context

- Consulted `metrics/statpack.md`. Its resolved First Circuit cut reports: `other` 86.3%, `dismissed` 8.0%, `denied` 5.0%, and `granted` 0.7% (599 resolved cases).
- Attempted `uv run fedcourts query --court ca1 --topic '3440 Other Civil Rights' --era 2010s --limit 10 --corpus-backend ranged`.
  - The command failed before returning priors because the corpus remote's host could not be resolved.
  - No `ranged corpus reads: …` line was printed.

## CourtListener MCP

- Attempted an opinions search limited to material filed before March 25, 2020, in the First Circuit and District of Puerto Rico for `"PROMESA" "automatic stay" appeal`.
  - The server returned `REDIS_URL is not set; cannot access session store.` No search results were consulted.

## Local interpretive materials

- Consulted `docs/data-pipeline.md`, `src/fedcourtsai/pipeline/events.py`, and `tests/test_events.py` to confirm that an entry-pinned petition event is meant to represent a request appearing in that docket entry. This supported the conclusion that the retrospective reference to the Commonwealth's Title III petition is structurally ambiguous as a petition-disposition target.

No web search was used, and this case's later docket, disposition, or subsequent history was not sought.
