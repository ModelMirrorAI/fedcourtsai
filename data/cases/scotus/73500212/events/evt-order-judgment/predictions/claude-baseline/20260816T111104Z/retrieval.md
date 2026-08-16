# Retrieval log (claude-baseline, 20260816T111104Z)

Beyond the provisioned inputs (snapshot 2026-08-16, `record/documents/`
petition / brief-in-opposition / questions-presented, `record/context.json`)
and the committed `metrics/statpack.md`:

1. `uv run fedcourts query --court scotus --citation "587 U.S. 554" --limit 3`
   (known-case lookup for Taggart v. Lorenzen, the controlling contempt
   precedent) — returned **no rows**.
   - stderr transfer line: `ranged corpus reads: 1329 GET(s), 348389376 byte(s)`
   - stderr coverage note: `citations filter: 161 of 590339 rows in scope
     (scotus) carry citation data, and the column holds a case's OWN reporter
     cites (not a cases-citing-this-authority graph) — an empty result here
     usually means missing data, not no match`
   - Per the coverage note this is a data gap, not an absent precedent; I did
     not retry sparse filters.

No CourtListener MCP lookups and no web searches — the provisioned cert-stage
documents (including the Ninth Circuit opinion appendix inside petition.txt)
covered the pre-decision record this forecast rests on.
