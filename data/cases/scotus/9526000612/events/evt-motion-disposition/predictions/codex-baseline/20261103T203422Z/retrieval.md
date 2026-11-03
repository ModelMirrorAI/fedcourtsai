# Retrieval log

No search targeted this application's disposition or subsequent history. The case-specific information used was exclusively provisioned.

## Local corpus tools

The first `uv run fedcourts paths --court scotus --docket 9526000612 --event evt-motion-disposition --role predictor` and `uv run fedcourts query --help` failed before execution because uv's default cache location was read-only. Both were retried successfully with `UV_CACHE_DIR=/tmp/fedcourts-uv-cache` and `uv run --no-sync`, using the already-provisioned environment without installing anything. The paths command identified the event and withheld the evaluator-only outcome. Query help was read twice, the second time as a narrower excerpt to inspect filters.

1. `UV_CACHE_DIR=/tmp/fedcourts-uv-cache uv run --no-sync fedcourts query --court scotus --disposition denied --era modern --decided-before 2026 --limit 5`
   - Refused: `modern` is not an era token. The tool supplied the accepted decade vocabulary. No transfer line was printed.
2. `UV_CACHE_DIR=/tmp/fedcourts-uv-cache uv run --no-sync fedcourts query --court scotus --disposition denied --era 2020s --decided-before 2026 --limit 5`
   - `ranged corpus reads: 14 GET(s), 3670016 byte(s)`
   - Returned Google LLC v. VirtaMove (25-1230), Hastings College Conservation Committee v. California (25-1231), Ryan O'Donnell v. City of Chicago (25-1098), Utah v. Mullins (25-1115), and Amy Hadley v. City of South Bend (25-1158). These are denied cert petitions, not application comparators; no calibration or doctrinal inference was drawn from them. The term cutoff concerns application/petition Term, not strictly the calendar year of every returned entry.
3. `UV_CACHE_DIR=/tmp/fedcourts-uv-cache uv run --no-sync fedcourts query --court scotus --citation '533 U.S. 1301' --decided-before 2026 --limit 2`
   - `ranged corpus reads: 8 GET(s), 2097152 byte(s)`
   - No results. The tool reported only 200 citation-bearing rows in scope and warned that empty results likely reflect sparse own-reporter-citation coverage. The precedent was available through MCP instead.

`metrics/statpack.md`, section "The interim docket (applications)," was consulted. It contains older-reading counts but not the finer-reading counts or unread checks required to calculate this cell's baseline. Its raw all-Term rate and cert statistics were not used as substitutes. Prediction and feedback schemas, relevant prompt sections, and the repository's Justice roster were read for output conformance; these are tooling references, not case evidence.

## CourtListener MCP

1. `search(type="o", court="scotus", q='"injunctive relief" "indisputably clear"', num_results=3, fields=["caseName", "dateFiled", "citation", "absolute_url", "opinions"])`
   - Returned two records for Brown v. Gilmore, 533 U.S. 1301 (September 12, 2001), and NFIB v. OSHA, 595 U.S. 109 (January 13, 2022). Only Brown was selected for a full read. Search query id: `cc8886d8`.
2. `read_document(opinion_id=9195259)`
   - Read Brown v. Gilmore in full (9,833 characters). Used only the in-chambers procedural distinction and extraordinary-injunction standard. Its underlying constitutional issue was not treated as analogous to this case.

## Web tool attempts

These calls returned no visible search results or page contents, so none supplied evidence:

1. Search batch: `site.supremecourt.gov in chambers injunction "indisputably clear" "Turner"`; `site.supremecourt.gov "Current Members" Supreme Court`.
2. Search batch: `site.supremecourt.gov "Turner v. Rogers" "indisputably"`; `site.supremecourt.gov/about/biographies.aspx`.
3. Open attempt: the Supreme Court's official Current Members biographies page.

The Turner phrasing was an unsuccessful exploratory search, not a cited authority. No statement about the governing standard rests on it. The output roster follows the contract and repository roster.
