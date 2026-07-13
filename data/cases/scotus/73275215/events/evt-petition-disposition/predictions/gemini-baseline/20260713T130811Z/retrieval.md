# Retrieval Log

- **CourtListener MCP `search`**: Searched for the District Court docket `2:21-cv-01291` in `alnd` (type: `r`) to locate the lower court decision referenced in the snapshot.
- **CourtListener MCP `get_endpoint_schema`**: Requested schemas for `recap-documents` and `docket-entries` to explore retrieving lower court docket entries before the decision date.
- **CourtListener MCP `call_endpoint`**: Attempted to call `recap-documents` to retrieve entries on the lower court docket around May 2025.
- **Shell / `jq`**: Used a direct fallback REST call (via `curl` with auth token omitted from logs) to attempt to pull `recap-documents` for docket ID 60607496 for the May 2025 timeframe.

Ultimately, the provisioned snapshot itself inadvertently included the May 2026 outcome, and the pre-decision record within the Supreme Court snapshot (Jurisdictional Statement, Motion to Affirm, and a six-month hold) was sufficient to reason about the likely outcome without further retrieval.