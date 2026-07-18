# Retrieval Log

- Examined the local `statpack.md` and `statpack.json` for base rates on Paid cert petitions and historical grant rates for the 2024 and 2025 Terms.
- Used `fedcourts query` to search for similar cases involving FRAP 4(a)(5):
  - `uv run fedcourts query --court scotus --topic "FRAP 4(a)(5)"`
    - `ranged corpus reads: 467 GET(s), 122421248 byte(s)`
  - `uv run fedcourts query --court scotus --disposition denied --topic "FRAP 4(a)(5)"`
    - `ranged corpus reads: 466 GET(s), 122159104 byte(s)`
- Used the CourtListener MCP `search` tool to look for dockets and opinions regarding FRAP 4(a)(5), excusable neglect, and good cause to assess the cited circuit split:
  - `search(court=["scotus"], q="\"Rule 4(a)(5)\" AND \"excusable neglect\" AND \"good cause\"", type="d")`
  - `search(court=["scotus"], q="\"Rule 4(a)(5)\" AND \"excusable neglect\"", type="o")` (Surfaced 6 opinions including *Hamer v. Neighborhood Housing Servs.* and *Pioneer Investment Services Co.*)
  - `search(court=["ca3"], docket_number="24-2794", type="d")` (No results)
  - `search(court=["ca3"], q="\"Mazza\" AND \"Bank of New York Mellon\"", type="o")` (No results)
  - `search(court=["ca3"], q="\"Mazza\" AND \"Mellon\"", type="o")` (Throttled/Rate Limited)
- Used the `google_web_search` tool to verify the context of the underlying litigation:
  - `google_web_search(query="\"Mark Mazza\" \"Bank of New York Mellon\" \"Third Circuit\"")` (Confirmed the case is a long-running, pro se foreclosure/ejectment dispute with multiple prior Third Circuit affirmances).