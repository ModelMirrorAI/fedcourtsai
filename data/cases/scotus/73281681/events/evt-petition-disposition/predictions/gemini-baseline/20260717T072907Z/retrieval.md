# Retrieval Log

### Provisioned Inputs
- Event definition: `data/cases/scotus/73281681/events/evt-petition-disposition/event.yaml`
- Baseline snapshot: `data/cases/scotus/73281681/record/snapshots/2026-07-17.json`
- Petition (`petition.txt`) and Questions Presented (`questions-presented.txt`)

### Corpus & Base Rates
- Read `metrics/statpack.md` to establish the baseline grant rate for modern discretionary cert petitions and to review the signal cuts for originating circuits. 
- Attempted to query the corpus via `fedcourts query --court scotus ...` but it errored due to a missing/unconfigured backend in the headless environment (no `corpus.db` and no `FEDCOURTS_CORPUS_SERVICE_URL`). Relied on MCP and `statpack.md` instead.

### CourtListener MCP
- `mcp_courtlistener_search(court="scotus", q='"Nollan" AND "Dolan" AND "Koontz"', type="o")` -> surfaced *Koontz v. St. Johns River Water Management Dist.*, *Sheetz v. El Dorado County*, and *Cedar Point Nursery v. Hassid*.
- `mcp_courtlistener_search(court="scotus", q='"SoHo" AND "NoHo"', type="d")` -> returned 0 results.
- `mcp_courtlistener_search(court="scotus", q='"Sheetz" AND "monetary demands"', type="o")` -> returned 0 results.