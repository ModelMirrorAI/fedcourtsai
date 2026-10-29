# Retrieval Log (`scotus/73500284` — `evt-order-call-for-response-disposition`)

- **Local Corpus Queries**:
  - None (`corpus/corpus.db` is not provisioned in this runner environment; only `corpus/corpus.db.ref` is present). Base rates were read directly from `metrics/statpack.md` and `metrics/statpack.json`.
- **CourtListener MCP Lookups**:
  - `mcp_courtlistener_search` (type `o`, `citation="590 U.S. 432"` for *GE Energy Power Conversion France SAS, Corp. v. Outokumpu Stainless USA, LLC*) — returned HTTP 429 daily rate-limit error (`Rate limit exceeded: 1400/day`).
  - `mcp_courtlistener_search` (type `o`, `citation="96 F.4th 726"` for *Bufkin Enterprises, L.L.C. v. Indian Harbor Insurance Co.*) — returned HTTP 429 daily rate-limit error (`Rate limit exceeded: 1400/day`).
  - `mcp_courtlistener_search` (type `o`, `citation="3 F.4th 1166"` for *Setty v. Shrinivas Sugandhalaya LLP*) — returned HTTP 429 daily rate-limit error (`Rate limit exceeded: 1400/day`).
  - `mcp_courtlistener_search` (type `o`, `case_name="Outokumpu Stainless USA Coverteam"`, `court="ca11"`) — returned HTTP 429 daily rate-limit error (`Rate limit exceeded: 1400/day`).
  - `mcp_courtlistener_extract_citations` (local eyecite extraction over the authorities cited in the Fifth Circuit's opinion in Appendix A) — succeeded locally and resolved 8 case citations (*Bufkin Enterprises*, *Arthur Andersen*, *GE Energy*, *InterGen*, *Smith/Enron*, *Aggarao*, *Setty*, and *Police Jury of Calcasieu Parish*).
- **Web Searches**:
  - None.
