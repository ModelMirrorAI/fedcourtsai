# Retrieval log — Nelsen v. Pike (26A428)

Beyond the provisioned inputs (`record/snapshots/2026-09-30.json`,
`record/context.json`, `record/documents/application.txt` and
`documents.json`, the event definition) and the committed
`metrics/statpack.md` (*The interim docket (applications)* section):

## Corpus

- `uv run fedcourts query --court scotus --include-applications --disposition granted`
  — 20 rows, all recent time-extension or unrelated stay grants (26A4xx
  series); no filter reaches state applications to vacate stays of execution,
  so nothing from this query informed the forecast.
  stderr: `ranged corpus reads: 7 GET(s), 1703936 byte(s)`

## CourtListener MCP

1. `search` (type `r`, court `ca6`, docket_number `26-5864`, q `Pike`) — found
   In re: Christa Pike, docket 74871499, with the Sept. 30 stay order
   (document 10, RECAP ids 495592156 and 495590629) and Pike's motion to
   remand (document 7, RECAP id 495590627).
2. `search` (type `r`, court `tned`, docket_number `1:12-cv-00035`, q `Pike
   Freeman`) — found the district-court habeas docket (Pike v. Johns), with the
   State's Sept. 29 motion to transfer (entry 118); document text not
   available.
3. `read_document` (recap_document_id 495590629) — read the Sixth Circuit's
   published order staying the execution (Stranch, J., joined by Moore, J.)
   and Judge Griffin's dissent, seven pages.
4. `call_endpoint` (`docket-entries`, docket 74871499) — eight entries through
   the Sept. 30 09:17 stay order; no later entry as of CourtListener's last
   poll.

No web searches. No lookup of this application's own disposition was made and
none surfaced.
