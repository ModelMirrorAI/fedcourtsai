# Retrieval Log

The following retrieval actions were conducted to inform the prediction for case `scotus/73272489` (Docket No. 25-1235):

---

## 1. CourtListener MCP Lookups

* **`mcp_courtlistener_search` (Type: `docket`, Number: `25-1235`, Court: `scotus`)**
  * *Result:* Validation error (incorrect type parameter). Corrected type to `"d"`.
* **`mcp_courtlistener_search` (Type: `d`, Number: `25-1235`, Court: `scotus`)**
  * *Result:* Failed due to missing upstream server configuration (`REDIS_URL is not set`).
* **`mcp_courtlistener_get_endpoint_item` (Endpoint: `dockets`, Item ID: `73272489`)**
  * *Result:* Successful. Retrieved the metadata for the target docket, identifying original court info ID `961910` and filing/modification dates.
* **`mcp_courtlistener_get_endpoint_item` (Endpoint: `originating-court-information`, Item ID: `961910`)**
  * *Result:* Successful. Retrieved the lower court case number `B334226` and decision dates (Judgment date: `2025-08-18`; Rehearing Denied: `2025-09-03`).

---

## 2. Google Web Searches

* **Query:** `"Leslie Sanders" "Long Beach" "B334226"`
  * *Result:* No matching results.
* **Query:** `"Leslie Sanders" "Long Beach"`
  * *Result:* Highly informative. Found news and summaries of the 2019 flooding event at Orangewood Village Townhomes, lawsuit details (Case No. 19STCV43406), and public advocacy details.
* **Query:** `site:supremecourt.gov "25-1235"`
  * *Result:* Returned application for extension in an unrelated case.
* **Query:** `"Leslie Sanders" "Long Beach" site:courtlistener.com`
  * *Result:* Found that the California Court of Appeal decision was unpublished (Rule 8.1115(a)), which is why it did not exist in CourtListener's database.
* **Query:** `"Leslie Sanders" "City of Long Beach" site:supremecourt.gov`
  * *Result:* Successful. Located the exact SCOTUS docket details showing postmarked/received dates and distribution for conference on June 17, 2026, without requesting a response.

---

## 3. Local/Remote Corpus Query Attempts (CLI)

* **Command:** `uv run fedcourts query --court scotus --limit 5`
  * *Result:* Failed. No local corpus file at `corpus/corpus.db` (DVC file not pulled).
* **Command:** `uv run fedcourts query --court scotus --corpus-backend ranged --limit 5`
  * *Result:* Failed. `RangedBackendError` due to missing DVC remote S3 environment variables.

---

## 4. Internal Statpack Resources

* **Path:** `metrics/statpack.md` and `metrics/statpack.json`
  * *Result:* Analyzed overall base rates for SCOTUS dockets, establishing that certiorari is denied or otherwise disposed of in the overwhelming majority of cases.
