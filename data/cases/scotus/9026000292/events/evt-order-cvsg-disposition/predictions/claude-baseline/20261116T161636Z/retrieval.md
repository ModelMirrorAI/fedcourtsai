# Retrieval log

- Provisioned inputs read: snapshot, context.json, event.yaml, documents (questions-presented, petition excerpts, lower-court-docket, documents.json), related/26-293.json, related/26-294.json, related.json, same-question.json. I also printed the top of `summaries/2026-11-15.md` in the case directory (a pipeline-written plain-language case summary, not a forecast).
- `metrics/statpack.md`: relist-count, CVSG-status and amicus-count cuts (paid scored segment).
- `uv run fedcourts query --help` (usage).
- `uv run fedcourts query --court scotus --disposition granted --era modern --limit 5` — returned only help/usage text (the `--era` value was not accepted); no rows.
- `uv run fedcourts query --court scotus --disposition granted --limit 5` — stderr: `ranged corpus reads: 33 GET(s), 8585216 byte(s)`; returned five recent granted dockets (Robinhood v. Sodha, Mullin v. RAICES, Mullin v. Friends of the Ruidosa Church, Goldman Sachs v. Brown, Scanlan v. Coalition for Open Democracy), none relevant to this question.
- No CourtListener MCP calls and no web searches.
