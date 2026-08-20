# Retrieval

- Consulted `metrics/statpack.md` and `metrics/statpack.json` for the modern-cert, Ninth Circuit, paid relist, paid CVSG, and `sal-v3` per-Term salience-band base rates. No corpus query was run.
- CourtListener MCP `get_endpoint_item`, `dockets`, item `73280982`, fields `id`, `docket_number`, `case_name`, `date_filed`, `date_terminated`, and `absolute_url`: the docket was unterminated.
- CourtListener MCP `get_endpoint_schema`, `docket-entries`: checked available fields and filters before querying.
- CourtListener MCP `call_endpoint`, `docket-entries`, docket `73280982`, dates on or after `2026-06-02`, fields `id`, `date_filed`, and `description`: no results.
- CourtListener MCP `call_endpoint`, `docket-entries`, docket `73280982`, all dates, fields `id`, `date_filed`, and `description`: no results, confirming that this endpoint did not expose the SCOTUS entries rather than showing an empty post-snapshot interval.
