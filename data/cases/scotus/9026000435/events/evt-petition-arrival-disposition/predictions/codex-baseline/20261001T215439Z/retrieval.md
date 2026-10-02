# Retrieval log

## Local materials beyond the provisioned record

- Read `metrics/statpack.md`: modern-cert disposition and originating-circuit sections, paid-segment relist and CVSG cuts, and the sal-v4 per-Term segment table. Read only the top-level key names of `metrics/statpack.json`; no additional numerical rates were taken from that file.
- Calculated the private baseline reached pool from displayed 2017–2025 rows with a local Python command: sum of displayed rate times weighted denominator, divided by sum of denominators; result approximately 0.05010888 over 12,720 weighted resolved cases. No corpus query was performed, so no ranged-read transfer line exists.
- Read the task contract and relevant output schemas. Ran `uv run fedcourts paths --court scotus --docket 9026000435 --event evt-petition-arrival-disposition --role predictor`. Its first invocation failed because the default uv cache was read-only; a temporary-cache override succeeded. This was path resolution, not a historical-case lookup.

## Web attempts

1. `web.search_query`: `site.supremecourt.gov opinions 2023 Loper Bright 22-451 factfinding policymaking deference`. No usable result was returned.
2. `web.open`: official Supreme Court opinion path `https://www.supremecourt.gov/opinions/23pdf/22-451_7m58.pdf`. No usable content was returned. Neither attempt supplied substantive evidence.

## CourtListener MCP

1. `search(type="o", citation="603 U.S. 369", num_results=1)`: located Loper Bright Enterprises v. Raimondo, decided June 28, 2024; cluster 10600041, opinion 11066629. I did not follow the returned citing-case metadata.
2. `search_document(opinion_id=11066629, query="policymaking", snippet_size=650)`: checked the majority's discussion at 603 U.S. 392 distinguishing independent statutory interpretation from deferential factual/policy review. Other returned excerpts did not inform case-specific facts.
3. `search(type="o", citation="303 F.3d 896", num_results=1, fields=["caseName", "dateFiled", "citation", "opinions", "absolute_url"])`: located Multimedia KSDK, Inc. v. NLRB, decided September 10, 2002; cluster 3029656 and lead opinion 9817149.
4. `read_document(opinion_id=9817149)`: read the Eighth Circuit majority concerning its producers' duties and the improper categorical exclusion of professional/technical judgment. Used to assess the petition's asserted split, not to infer Nexstar's outcome.

No live Nexstar docket, outcome, subsequent history, other predictor output, or labeling artifact was retrieved.
