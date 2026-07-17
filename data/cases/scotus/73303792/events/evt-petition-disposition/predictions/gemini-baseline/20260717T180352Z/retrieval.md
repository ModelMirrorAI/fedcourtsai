# Retrieval Log

- **CourtListener MCP (`search` and `call_endpoint`):**
  - Searched the Sixth Circuit and Ohio State court opinions for cases involving "John Paul Gomez" and "David Ryan" to identify the nature of the underlying dispute (`q="John Paul Gomez" "David Ryan"`). 
  - Searched by docket number "24-3840" on the Sixth Circuit to retrieve the docket ID (69636140).
  - Queried `docket-entries` for the Sixth Circuit docket ID 69636140 to view the activity on the lower court docket.
  - Queried `opinions` for the Sixth Circuit docket ID to attempt to read the lower court decision.

- **Web Search (`google_web_search`):** 
  - Conducted a web search (`"John Paul Gomez" "David Ryan" Sixth Circuit`) to summarize the facts of the lower court decision, as the provisioned petition document was empty (due to `empty_text: true`) and the Sixth Circuit opinion was not available directly through the CourtListener search endpoint. This confirmed the case is a § 1983 action against police and judicial officials, dismissed on qualified immunity, judicial immunity, and Rooker-Feldman grounds.

- **Corpus Base Rates:** 
  - Checked `metrics/statpack.md` (via `grep` and `cat`) to review base rates for modern cert petitions, noting the low base rate (~2.5-3%) for paid petitions.
