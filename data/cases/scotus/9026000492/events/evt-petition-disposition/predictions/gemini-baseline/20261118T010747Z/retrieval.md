# Retrieval Log

All external/corpus lookups performed beyond the provisioned case files (`record/`) and committed `metrics/statpack.md`:

## 1. Local / Ranged Corpus Lookups (`fedcourts`)

1. `uv run fedcourts query --court scotus --citation "592 U.S. 351" --limit 10`
   - Stderr read stats: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Result: Returned 0 rows, with CLI note explaining that `--citation` matches a case's own parallel reporter citations rather than a citing-cases graph and only 195 SCOTUS rows in scope carry reporter citations.
2. `uv run fedcourts query --court scotus --era 2020s --decided-before 2026 --limit 10`
   - Stderr read stats: `ranged corpus reads: 26 GET(s), 6815744 byte(s)`
   - Result: Returned 10 recent resolved pre-OT2026 SCOTUS cert rows (Nos. 25-1238, 25-1240, 25-1303, 25-1324, 25-7485, 25-7562, 25-1421, 25-7667, 25-944, 25-442), confirming `sal-v8` scoring metadata and that state intermediate appellate courts populate `originating_court: null` with full court names in `originating_court_name`.

*(Non-retrieval CLI helper commands also run: `uv run fedcourts paths --court "scotus" --docket "9026000492" --event "evt-petition-disposition" --role predictor`, `uv run fedcourts query --help`, and post-write `uv run fedcourts validate data --cell ...`.)*

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search` (`type="o"`, `q='"Ford Motor" "Bristol-Myers" "nonresident plaintiffs" "relate to"'`, `filed_after="2021-03-25"`, `order_by="citeCount desc"`, `num_results=10`)
   - Result: `count=19` published appellate/district opinions returned (led by *Canaday v. The Anthem Companies, Inc.*, 9 F.4th 392 (6th Cir. 2021), *Fischer v. Federal Express Corp.* (3d Cir.), *Waters v. Day & Zimmermann NPS, Inc.* (1st Cir.), and state/federal personal-jurisdiction rulings), confirming that post-*Ford* appellate courts consistently maintain *Bristol-Myers Squibb*'s bar on claims by nonresident plaintiffs injured outside the forum State.
2. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `q='"personal jurisdiction" "Fourteenth Amendment"'`, `filed_after="2023-06-01"`, `fields=["caseName", "citation", "dateFiled", "docketNumber", "syllabus"]`, `num_results=20`)
   - Result: `count=15` SCOTUS opinion clusters returned (including *Fuld v. Palestine Liberation Organization*, 606 U.S. 1 (2025), decided June 20, 2025 on Fifth Amendment due process grounds, and *Mallory v. Norfolk Southern Railway Co.*, 600 U.S. 122 (2023), decided June 27, 2023), confirming no intervening post-December 2025 SCOTUS Fourteenth Amendment corporate specific-jurisdiction holding exists to support a GVR.

## 3. Web Searches

None attempted.
