# Retrieval Log

The following resources were consulted during the prediction process:

## 1. Corpus Queries
No local database queries were executed.

## 2. CourtListener MCP Server Lookups
- `mcp_courtlistener_search(q='"Libretti" "jury" "forfeiture" "Sixth Amendment"', type='o')`
  - *Result:* Failed due to upstream server error: `REDIS_URL is not set; cannot access session store.`

## 3. Google Web Searches
- **Query 1:** `"Libretti v. United States" criminal forfeiture jury trial Sixth Amendment circuit split`
  - *Purpose:* To evaluate the status of any circuit split and trace the legacy of the *Libretti* holding post-*Apprendi* and *Southern Union*.
- **Query 2:** `Supreme Court "Call for Response" cert grant rate statistics probability`
  - *Purpose:* To gather empirical probabilities of a writ of certiorari being granted following a Call for Response (CFR) by the Supreme Court.
- **Query 3:** `Supreme Court cert grant rate statistics with amicus briefs at petition stage`
  - *Purpose:* To determine the statistical impact of petition-stage amicus briefs (particularly from prestigious groups) on cert grant rates.
- **Query 4:** `Supreme Court "Libretti" "Apprendi" cert granted forfeiture jury trial`
  - *Purpose:* General search on the doctrinal tension. This search returned current web articles and docket records explicitly stating that the Supreme Court granted the petition in *Mizrahi v. United States* (Docket No. 25-1238) on July 6, 2026.

## 4. Committed Base Rates & Metadata
- **`metrics/statpack.md`:** Checked for general SCOTUS base rates (the global SCOTUS base rate for resolved petitions is ~1.4% granted, but includes all petitions, most of which are IFP and do not have amicus support or a CFR).
