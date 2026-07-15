# Retrieval Log

1. **Base Rates (Statpack):**
   - Read `metrics/statpack.md` section "Modern discretionary-cert petitions by disposition" and "by originating circuit". 
   - Found the overall grant rate for modern cert petitions is very low (around 3%), and for the Second Circuit (ca2) it is approximately 5.4%.

2. **Corpus Query CLI:**
   - Attempted `fedcourts query` for "assault weapon" but failed due to syntax (it expects structured filters, not keywords).

3. **CourtListener MCP:**
   - Call: `mcp_courtlistener_search` with query `"assault weapon" OR "AR-15" OR "large capacity magazine" AND "Second Amendment"`, type `d`.
   - Call: `mcp_courtlistener_search` with query `"assault weapon" OR "AR-15"`, type `d`.
   - Purpose: To identify other pending or recently decided AWB cases that might serve as lead cases (e.g., *Snope*, *Bevis*, *Antonyuk*).

4. **Web Search:**
   - Call: `google_web_search` with query `Supreme Court Second Amendment assault weapons ban 2025 2026`.
   - Purpose: To check if the Court had recently granted cert in any AWB cases, explaining why this petition was held 17 times.
   - Result: Discovered that on June 30, 2026, the Court granted review in *Viramontes v. Cook County* and *Grant v. Higgins*.
