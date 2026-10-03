# Retrieval log

Beyond the provisioned inputs (snapshot `2026-10-03.json`, `context.json`,
`event.yaml`, `questions-presented.txt`, `petition.txt`,
`brief-in-opposition.txt`) and the committed `metrics/statpack.md`:

## Corpus lookups (`fedcourts`)

1. `uv run fedcourts paths --court scotus --docket 73500234 --event evt-petition-disposition --role predictor`
   (path resolution only; no transfer line).
2. `uv run fedcourts query --court scotus --citation '598 U.S. 152' --limit 3`
   stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   Result: empty; `note:` line reported only 200 scotus rows carry any
   reporter citation, so the column could not serve the lookup.
3. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   stderr: `ranged corpus reads: 5 GET(s), 1310720 byte(s)`
   Result: five recent granted rows (two cert petitions granted 2026-10-01 off
   the 2026-09-28 conference, two substantive applications, one petition
   granted alongside an application). None on a comparable subject; used only
   as shape context for the first-conference grant pattern.

(A first `query` attempt with a free-text argument was rejected by the CLI,
which takes flags only; no corpus read occurred.)

## CourtListener MCP lookups

1. `search` type=o, court=ca9, q=`Wilkins "Quiet Title Act" "law of the case" "Robbins Gulch"`,
   filed 2025-12-01 to 2026-01-31. One hit: *Wilkins v. United States*,
   docket 25-37, filed 2025-12-29, status Published. Used only to confirm
   the decision below is published; the opinion text was not read.

## Web searches

None.
