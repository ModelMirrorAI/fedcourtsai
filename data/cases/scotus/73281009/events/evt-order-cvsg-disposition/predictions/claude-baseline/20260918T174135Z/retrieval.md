# Retrieval log

## Corpus tooling
- `uv run fedcourts query --court scotus --era 2020s --disposition granted`
  stderr: `ranged corpus reads: 47 GET(s), 12320768 byte(s)`
  (recent granted priors; none a CVSG'd election-law cert petition — used only as a
  sanity check on the corpus's recent slice)
- `metrics/statpack.md` (committed): modern cert by disposition; relist-count and
  CVSG cuts (paid scored segment); salience-band cuts; per-Term table; segment base
  rate by salience band (sal-v4).

## CourtListener MCP
- `search` type=docket, court=scotus, docket_number=25-962 — 0 results (companion
  docket not indexed).

## Web (forward mode; this case's own disposition checked and found absent)
- supremecourt.gov docket 25-967 — no entries after 2026-06-29; no SG brief; pending.
- supremecourt.gov docket 25-962 (RNC v. Eakin) — same CVSG 2026-06-29; pending.
- scotusblog.com case page for 25-967 — pending; nothing after the CVSG.
- WebSearch: Baxter v. Philadelphia Board of Elections status (three queries); pages
  read: aclupa.org case page (latest entry Sept. 2025 argument notice, no decision),
  democracydocket.com case page (pending), statecourtreport.org tracker (its summary
  conflated Coalfield Justice with Baxter; treated as no evidence of a Baxter ruling).
- democracydocket.com news alert on the CVSG (2026-06-29) — commentary only.
- spotlightpa.org (2026-09) — confirmed the September 2026 Supreme Court mail-voting
  ruling concerns the Trump executive order on postal handling of ballots, not this
  petition.
- electionlawblog.org post on the CVSG and penncapital-star.com — HTTP 403, not read.
