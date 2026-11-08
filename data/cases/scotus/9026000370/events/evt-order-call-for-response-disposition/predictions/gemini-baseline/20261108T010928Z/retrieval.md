# Retrieval Log

## Corpus Queries (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer: `ranged corpus reads: 40 GET(s), 10485760 byte(s)`
   - Result: Returned 10 recent OT2026 granted SCOTUS petitions/applications (`scotus/9526000512`, `scotus/9026000012`, `scotus/9026000204`, `scotus/9526000476`, `scotus/73281386`, `scotus/73283862`, `scotus/73500246`, `scotus/73281619`, `scotus/73500251`, `scotus/9026000104`).

2. `uv run fedcourts query --court scotus --citation "555 U.S. 438" --citation "540 U.S. 398" --citation "547 U.S. 28" --limit 10`
   - Transfer: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Result: Empty (printed note on sparse `citations` column coverage on SCOTUS rows).

3. `uv run fedcourts query --court scotus --docket-number "26-370"`
   - Transfer: `ranged corpus reads: 13 GET(s), 3407872 byte(s)`
   - Result: Returned the corpus metadata row for `scotus/9026000370` (*The Nielsen Company (US), LLC v. Cumulus Media New Holdings Inc.*).

## CourtListener MCP Lookups

1. `mcp_courtlistener_search` (`type="o"`, `citation="555 U.S. 438"`, `fields=["caseName", "citation", "dateFiled", "cluster_id"]`)
   - Result: *Pacific Bell Telephone Co. v. Linkline Communications, Inc.*, 555 U.S. 438 (2009) (`cluster_id: 145906`).

2. `mcp_courtlistener_search` (`type="o"`, `citation="547 U.S. 28"`, `fields=["caseName", "citation", "dateFiled", "cluster_id"]`)
   - Result: *Illinois Tool Works Inc. v. Independent Ink, Inc.*, 547 U.S. 28 (2006) (`cluster_id: 145674`).

3. `mcp_courtlistener_search` (`type="o"`, `citation="549 F.3d 1097"`, `fields=["caseName", "citation", "dateFiled", "cluster_id"]`)
   - Result: 1 unrelated district court match (`cluster_id: 2355828`).

4. `mcp_courtlistener_search` (`type="o"`, `citation="515 F.3d 883"`, `fields=["caseName", "citation", "dateFiled", "cluster_id"]`)
   - Result: *Cascade Health Solutions v. PeaceHealth*, 515 F.3d 883 (9th Cir. 2008) (`cluster_id: 3051039`).

5. `mcp_courtlistener_search` (`type="o"`, `citation="324 F.3d 141"`, `fields=["caseName", "citation", "dateFiled", "cluster_id"]`)
   - Result: *LePage's Inc. v. 3M*, 324 F.3d 141 (3d Cir. 2003) (`cluster_id: 781392`).
