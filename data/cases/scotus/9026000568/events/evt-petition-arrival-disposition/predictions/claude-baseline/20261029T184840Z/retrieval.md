# Retrieval log

- Web search: "Rhoney v. Barbosa da Cunha certiorari granted 1225(b)(2)(A)". Confirmed that No. 26-104 was granted Oct 1, 2026, on the government's petition from the Second Circuit, on the identical QP.
- `uv run fedcourts query --court scotus --docket-number 26-104`. Returned the lead case's row (granted 2026-10-01, ca2, federal petitioner, no merits judgment).
  `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
- `uv run fedcourts query --court scotus --disposition gvr --era modern --limit 5`. Refused because `modern` is not an era token (usage error, no rows). Not retried.
- `uv run fedcourts query --help`. Help text only.
- Statpack: `metrics/statpack.md`, the "Segment base rate by salience band (sal-v4)" table.
- No CourtListener MCP calls.
