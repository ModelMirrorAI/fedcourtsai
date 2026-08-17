# Retrieval log

Beyond the provisioned inputs (snapshot `2026-08-16.json`; `record/documents/`
petition, brief-in-opposition, and questions-presented texts; the committed
`metrics/statpack.md` merits section):

1. `fedcourts query --court scotus --citation "597 U.S. 1" --citation
   "554 U.S. 570" --citation "602 U.S. 680" --citation "561 U.S. 742"
   --citation "577 U.S. 411" --limit 8` — a known-case lookup of the modern
   Second Amendment merits line (*Bruen*, *Heller*, *Rahimi*, *McDonald*,
   *Caetano*). Returned **no rows**; stderr:
   - `ranged corpus reads: 1329 GET(s), 348389376 byte(s)`
   - `note: citations filter: 161 of 590339 rows in scope (scotus) carry
     citation data, and the column holds a case's OWN reporter cites (not a
     cases-citing-this-authority graph) — an empty result here usually means
     missing data, not no match`

   Read as a coverage gap per the note; not retried.

No CourtListener MCP calls and no web searches were made. The case's own
disposition was not sought (it does not exist — the grant is six weeks old
and merits briefing has not begun).
