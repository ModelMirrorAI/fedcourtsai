# Retrieval Log

## 1. Corpus Queries (`fedcourts`)

- `uv run fedcourts paths --court scotus --docket 9026000245 --event evt-order-cvsg-disposition --role predictor`
  - Resolved case, corpus, and event paths.
- `uv run fedcourts query --court scotus --docket-number 23-9`
  - `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
  - Retrieved the prior certiorari petition in this exact litigation (`scotus/72483367`, *AstraZeneca UK Limited, et al. v. Joshua Atchley, et al.*, No. 23-9, filed 2023-07-05, `cvsg_date: 2023-10-02`, `date_cert_granted: 2024-06-24`, `disposition: gvr`, `distribution_count: 2`).

## 2. CourtListener MCP Lookups

- `mcp_courtlistener_search(type="o", case_name="Ashley v. Deutsche Bank", filed_before="2026-11-10", fields=["caseName", "dateFiled", "court", "docketNumber", "citation", "cluster_id"])`
  - Returned 0 matches in the search index (the opinion, *Ashley v. Deutsche Bank Aktiengesellschaft*, 144 F.4th 420 (2d Cir. 2025), is extensively quoted and analyzed in the provisioned petition, brief in opposition, cert reply, and decision below).
- `mcp_courtlistener_search(type="o", q=""144 F.4th 420"", filed_before="2026-11-10", fields=["caseName", "dateFiled", "court", "docketNumber", "citation", "cluster_id"])`
  - Returned 0 matches in the search index.
