# Retrieval

- Read committed base-rate context from `metrics/statpack.md`. Relevant calibration: overall resolved SCOTUS rows show granted outcomes as uncommon relative to denied, dismissed, and other outcomes; the SCOTUS row reports a 1.4% granted resolved base rate. No ranged corpus read line applies because this was a committed artifact read from the working tree.
- No `fedcourts query` or `fedcourts open-events` corpus lookup was used. The snapshot is a sparse SCOTUS docket with no same-case exclusion available in the query interface, so I avoided any query that might inadvertently surface this case's own disposition.
- No CourtListener MCP lookup was used.
- No web search was used.
