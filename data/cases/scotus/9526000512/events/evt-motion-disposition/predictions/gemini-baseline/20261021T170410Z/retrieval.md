# Retrieval Log

## 1. Corpus Queries (`fedcourts`)

- `uv run fedcourts paths --court "scotus" --docket "9526000512" --event "evt-motion-disposition" --role predictor`
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --include-applications --limit 10`
  - `ranged corpus reads: 15 GET(s), 3932160 byte(s)`
- `uv run fedcourts query --court scotus --era 2020s --disposition denied --include-applications --limit 10`
  - `ranged corpus reads: 6 GET(s), 1572864 byte(s)`

## 2. CourtListener MCP Lookups

- `mcp_courtlistener_search` (`type="r"`, `case_name="Coalition for Open Democracy v. Scanlan"`): located First Circuit docket `26-2132` (`docket_id=74929205`).
- `mcp_courtlistener_search` (`type="o"`, `case_name="Coalition for Open Democracy v. Scanlan"`): located District of New Hampshire TRO opinion (`cluster_id=10695785`).
- `mcp_courtlistener_search` (`type="o"`, `case_name="People Not Politicians v. Onder"`): located SCOTUS opinion (`cluster_id=10984030`, `opinion_id=11451693`) and read via `mcp_courtlistener_read_document`.
- `mcp_courtlistener_search` (`type="o"`, `case_name="National Republican Congressional Committee v. Brown"`): located SCOTUS opinion (`cluster_id=10967483`, `opinion_id=11435097`) and read via `mcp_courtlistener_read_document`.
- `mcp_courtlistener_search` (`type="r"`, `court="nhd"`, `docket_number="1:26-cv-00647"`): located District of New Hampshire docket (`docket_id=74220507`).
- `mcp_courtlistener_call_endpoint` (`endpoint_id="docket-entries"`, `docket=74220507` and `docket=74929205`): listed docket entries in the District of New Hampshire and First Circuit.
- `mcp_courtlistener_get_endpoint_item` (`endpoint_id="docket-entries"`, `item_id=480696670`, `480882029`, `481452984`, `481233246`): retrieved District Court preliminary injunction order (Dkt. 68), District Court order denying stay (Dkt. 72), Appellee's First Circuit response opposing stay, and Appellants' First Circuit reply brief in support of stay.
- `mcp_courtlistener_search` (`type="r"` and `type="o"`, `case_name="New Hampshire Youth Movement v. Scanlan"`): checked related First Circuit docket (`26-1740`, `docket_id=73518816`) and District of New Hampshire docket (`1:24-cv-00291`, `docket_id=69168613`).
