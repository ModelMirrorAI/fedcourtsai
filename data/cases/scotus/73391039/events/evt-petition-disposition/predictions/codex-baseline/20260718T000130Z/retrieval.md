# Retrieval

- Read the committed `metrics/statpack.md` and `metrics/statpack.json` for modern cert, Eleventh Circuit, relist, CVSG, and 2025-Term paid-petition base rates. No `fedcourts query` or `fedcourts open-events` command was run, so there is no ranged-corpus-read line.
- CourtListener MCP opinion search for `Foley Orange County` in the Eleventh Circuit, limited to filings before July 18, 2026: found *Foley v. Orange County*, 638 F. App'x 941 (11th Cir. 2016).
- CourtListener MCP opinion search for docket `24-14143`: no result.
- CourtListener MCP opinion search for `"David W. Foley" "Orange County"`: returned the 2016 opinion.
- CourtListener MCP RECAP searches for docket `24-14143` and the parties: the exact-docket search returned no document; the broader party search returned no useful current-case document.
- CourtListener MCP opinion endpoint lookup for opinion id `8679403`: read the 2016 Eleventh Circuit opinion.
- CourtListener MCP docket searches for `24-14143`: two attempts were transiently throttled; a retry found Eleventh Circuit docket id `71794325`, *David Foley, Jr. v. Orange County*.
- CourtListener MCP docket and docket-entry schema lookups, followed by a docket-entry query for docket id `71794325`: found the October 29, 2025 opinion entry, but CourtListener had no available document text.
- Fetched the exact pre-decision Supreme Court petition PDF URL already listed in provisioned `documents.json` and visually read its 37 rendered pages because the provisioned scan had no text layer. This retrieval did not seek or surface the petition's disposition.
- No general web search was used.
