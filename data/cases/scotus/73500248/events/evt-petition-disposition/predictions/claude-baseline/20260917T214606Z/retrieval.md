# Retrieval log

## Corpus tooling

- `uv run fedcourts paths --court scotus --docket 73500248 --event evt-petition-disposition --role predictor`
- `uv run fedcourts query --court scotus --citation "583 U.S. 220" --limit 3`
  - stderr: `ranged corpus reads: 1357 GET(s), 355663872 byte(s)`
  - stderr note: `citations filter: 200 of 590940 rows in scope (scotus) carry citation data ...`
  - 0 rows returned (Murphy v. Smith not found by citation; coverage gap).
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
  - stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
  - 5 rows returned (People Not Politicians v. Onder; NRCC v. Brown; National Park
    Service v. National Trust for Historic Preservation; one further substantive
    application; Jouppi v. Alaska). Not comparable to this cert petition; not used
    beyond confirming the service responded.
- Base rates: committed `metrics/statpack.md` (modern discretionary-cert section,
  relist-count / CVSG / originating-circuit cuts, sal-v4 segment base rate by band).

## CourtListener MCP

1. `search` (type `o`, court `ca2`, q `Webb Trombley 1997e(d)(2) Shepherd Goord`,
   filed after 2025-01-01): 0 results. The summary order below was read from the
   petition appendix instead.
2. `search` (type `o`, court `scotus`, q `"1997e(d)(2)" "150 percent"`): 1 result,
   Murphy v. Smith, 583 U.S. 220 (2018), cluster 4469601, opinion 4246854.
3. `call_endpoint` `docket-entries` for docket 73500248: 0 results (CourtListener
   holds no entries for this SCOTUS docket).
4. `read_document` opinion 4246854, chunks 1-2 (6000 chars): Murphy majority, parts
   I-II.
5. `read_document` opinion 4246854, chunks 3-4: Murphy majority conclusion and
   footnote 2 (drafting history of the second sentence), start of the Sotomayor
   dissent.

## Web search

None.
