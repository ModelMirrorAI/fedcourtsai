# Retrieval

- `uv run fedcourts query --docket-number 22-240` failed with a usage error (it needs `--court`). No reads were made.
- `uv run fedcourts query --court scotus --docket-number 22-240` returned
  `ranged corpus reads: 18 GET(s), 4718592 byte(s)`. This is the earlier petition in the same litigation (Justice v. Jonathan R.), denied 2022-10-11.
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5` failed with a usage error (unknown era). No reads were made.
- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5` returned
  `ranged corpus reads: 28 GET(s), 7340032 byte(s)`. These were generic recent grants and did not inform the number.
- Read the committed `metrics/statpack.md` (salience band, relist, CVSG and amicus cuts).
- No CourtListener MCP or web retrieval.
