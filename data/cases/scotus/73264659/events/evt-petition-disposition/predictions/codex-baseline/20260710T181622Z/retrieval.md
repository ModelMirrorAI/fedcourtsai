# Retrieval

Provisioned inputs consulted:

- `data/cases/scotus/73264659/events/evt-petition-disposition/event.yaml`
- `data/cases/scotus/73264659/record/snapshots/2026-07-10.json`
- `data/cases/scotus/73264659/record/documents/documents.json`
- `data/cases/scotus/73264659/record/documents/questions-presented.txt`
- `data/cases/scotus/73264659/record/documents/petition.txt`
- `data/cases/scotus/73264659/record/context.json`

Additional retrieval consulted:

- Base rates: `metrics/statpack.md` and `metrics/statpack.json`.
- Corpus lookup attempted: `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '47 U.S.C. § 230' --limit 5 --corpus-backend ranged`
  - No `ranged corpus reads: ...` line was printed. The command failed before returning priors because DNS/network access to the ranged corpus remote was unavailable in this sandbox (`Name or service not known`).

CourtListener MCP lookups: none.

Web searches: none.
