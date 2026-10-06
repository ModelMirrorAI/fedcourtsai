# Retrieval log

Forward cell. Retrieval beyond the provisioned inputs:

## Corpus tooling

- `uv run fedcourts paths --court scotus --docket 9026000023 --event evt-petition-disposition --role predictor` (path resolution; no transfer line).
- `uv run fedcourts query --court scotus --citation "571 U.S. 69" --limit 8`
  stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
  Result: empty, with the tool's `note:` that only 200 SCOTUS rows carry any reporter citation. No priors used.
- `metrics/statpack.md` (committed): modern-cert disposition, originating-circuit, relist, CVSG, and sal-v4 band tables.

## CourtListener MCP (11 calls)

1. `search` dockets, court scotus, q "TitleMax Spicher": 0 results.
2. `search` opinions, courts ca5+ca3, q "TMX OR TitleMax Spicher Younger", filed after 2025-06-01: 0 results.
3. `call_endpoint` dockets, court scotus, docket_number 25-1359: found docket id 73500260 (TitleMax of Virginia v. Spicher, filed 2026-06-08, not terminated).
4. `search` opinions, ca5, docket_number 24-11087: 0 results (Fifth Circuit opinion not indexed).
5. `search` opinions, ca3, docket_number 25-1137: 0 results.
6. `call_endpoint` docket-entries for docket 73500260: 0 entries.
7. `search` opinions, ca5, case_name "TMX Finance", filed after 2025-12-01: 0 results.
8. `search` opinions, ca4, q "TitleMax Spicher", filed after 2025-08-01: 1 result, TitleMax of South Carolina v. Spicher, No. 25-2027, filed 2026-08-05, published (cluster 10941484).
9. `call_endpoint` dockets, court scotus, docket_number 25-170: Suncor Energy v. Boulder County, argued 2026-10-05, not terminated.
10. `get_endpoint_item` clusters 10941484: sub-opinion 11409067.
11. `read_document` opinion 11409067, chunks 0-1 and 4-9 (two calls): the Fourth Circuit's Younger analysis, in particular the important-state-interest section distinguishing Harper.

## Web fetch (1 call)

- `https://www.supremecourt.gov/docket/docketfiles/html/public/25-1359.html`: companion docket proceedings (petition filed Jun 3 2026; waiver Jul 8; South Carolina amicus Jul 8; distributed Jul 15 for Sep 28; response requested Jul 29; extensions to Nov 2 2026; no disposition shown).

Nothing retrieved concerned this petition's own disposition. The local repository case `scotus/72470586` was inspected only to the extent of its `event.yaml` title, which identified it as the 2022 TitleMax of Delaware v. Vague petition rather than the companion; nothing further was read there.
