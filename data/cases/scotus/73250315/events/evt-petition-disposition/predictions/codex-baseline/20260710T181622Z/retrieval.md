# Retrieval

## Provisioned Inputs

- `data/cases/scotus/73250315/events/evt-petition-disposition/event.yaml`
- `data/cases/scotus/73250315/record/context.json`
- `data/cases/scotus/73250315/record/snapshots/2026-07-10.json`
- `data/cases/scotus/73250315/record/documents/documents.json`
- `data/cases/scotus/73250315/record/documents/questions-presented.txt`
- `data/cases/scotus/73250315/record/documents/petition.txt`

## Base Rates

- Consulted `metrics/statpack.md`, especially the broad SCOTUS petition rows. The rendered statpack available in this checkout did not contain the named modern discretionary-cert heading from the prompt.

## Corpus Queries

- `uv run fedcourts query --court scotus --citation "United States v. Resendiz-Ponce" --citation "Russell v. United States" --limit 8 --corpus-backend ranged`
  - No `ranged corpus reads: ...` line was printed. The command failed before returning rows because remote corpus access could not resolve the remote host: `gaierror: [Errno -2] Name or service not known`.
- `uv run fedcourts query --court scotus --disposition granted --limit 8 --corpus-backend ranged`
  - No `ranged corpus reads: ...` line was printed. The command failed before returning rows because remote corpus access could not resolve the remote host: `gaierror: [Errno -2] Name or service not known`.

## CourtListener MCP

- No CourtListener MCP lookup was available through the exposed tool interface in this run.

## Web

- No web searches were used.
