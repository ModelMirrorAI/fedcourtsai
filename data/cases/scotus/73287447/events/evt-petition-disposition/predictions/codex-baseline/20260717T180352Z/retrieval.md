# Retrieval

- Repository base-rate sources: `metrics/statpack.md` and `metrics/statpack.json`, including modern discretionary-cert disposition, originating-circuit, relist, CVSG, Term 2025, and paid-fee-class statistics.
- Repository methodology source: `docs/salience.md`, consulted for the interpretation of relist, CVSG, fee-class, and selected-slice signals.
- CourtListener MCP opinion search: `q="\"nonpurchaser\" \"antitrust standing\""`, opinions filed before 2026-07-18, 10-result limit. It returned the Second Circuit decision below, *City of Oakland v. Oakland Raiders*, *Montreal Trading Ltd. v. Amax Inc.*, and three additional results.
- CourtListener MCP opinion search: `q="\"priced out\" \"antitrust standing\" -Nexstar"`, opinions filed before 2026-07-18, 10-result limit. It returned *City of Oakland*, *Knevelbaard Dairies v. Kraft Foods, Inc.*, and *Reazin v. Blue Cross & Blue Shield of Kansas, Inc.*
- CourtListener MCP item lookup: opinion item 10759121. The website search result's URL identifier was a cluster identifier rather than an opinion-record identifier, so this lookup returned unrelated *State v. Bates* material; it was disregarded.
- CourtListener MCP item lookup: cluster 10759121, limited to identifying fields and sub-opinions, to resolve the Second Circuit decision below to opinion record 11225706.
- CourtListener MCP item lookup: opinion 11225706, including the combined majority and dissent text in *DirecTV, LLC v. Nexstar Media Group, Inc.* This confirmed the pleading-stage posture, the majority's course-of-dealing rationale, Judge Sullivan's dissent, and the United States' amicus participation below.

No `fedcourts query` or `fedcourts open-events` corpus lookup was used, and no web search was used.
