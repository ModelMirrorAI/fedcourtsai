# Retrieval Log

## 1. Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Stderr transfer line: `ranged corpus reads: 32 GET(s), 8388608 byte(s)`
   - Purpose: Inspect recent 2020s SCOTUS granted docket rows and corpus schema fields.

*(Note: An initial attempt `uv run fedcourts query search "prerelease custody" --court ca5 --court ca8 --court scotus --limit 10` exited with usage error code 2 before any corpus read because `fedcourts query` accepts structured flags only.)*

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search` (`type="o"`, `case_name="Melot v. Bergami"`, `fields=["caseName", "citation", "court_id", "dateFiled", "cluster_id", "opinions"]`)
   - Returned Fifth Circuit decision *Billy Melot v. Thomas Bergami*, 970 F.3d 596 (5th Cir. 2020) (`cluster_id=4399722`, `opinion_id=4556672`), the precedent relied upon by the Fifth Circuit panel below.
2. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `case_name="Jones v. Hendrix"`, `fields=["caseName", "citation", "court_id", "dateFiled", "cluster_id", "opinions"]`)
   - Returned Supreme Court decision *Jones v. Hendrix*, 599 U.S. 465 (2023) (`cluster_id=10049669`, `opinion_id=10516269`).
3. `mcp_courtlistener_search` (`type="o"`, `case_name="Woodall v. Federal Bureau of Prisons"`)
   - Returned HTTP 429 rate-limit error (25/min); did not retry because *Woodall* is extensively quoted in both provisioned merits briefs.
4. `mcp_courtlistener_read_document` (`opinion_id=4556672`)
   - Read the full opinion in *Melot v. Bergami*, 970 F.3d 596 (5th Cir. 2020), verifying how the Fifth Circuit formulated its bright-line rule relegating home-detention claims to *Bivens*.
5. `mcp_courtlistener_search_document` (`opinion_id=10516269`, `query="place or manner not authorized"`)
   - Returned 0 matches due to hyphenation across line breaks in the slip opinion (`detained in a place or manner not
authorized`).
6. `mcp_courtlistener_search_document` (`opinion_id=10516269`, `query="good-time credits"`)
   - Matched the passage in *Jones v. Hendrix*, 599 U.S. at 475, listing § 2241 examples ("detained in a place or manner not authorized by the sentence, that he has unlawfully been denied parole or good-time credits, or that an administrative sanction affecting the conditions of his detention is illegal").

## 3. Web Searches

None.
