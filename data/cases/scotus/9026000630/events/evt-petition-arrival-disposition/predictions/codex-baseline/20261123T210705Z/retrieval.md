## Corpus and statistical sources

- `uv run fedcourts query --help` supplied the filter syntax. The initial `uv run fedcourts paths --court scotus --docket 9026000630 --event evt-petition-arrival-disposition --role predictor` failed to initialize the default uv cache. It succeeded with `UV_CACHE_DIR=/tmp/uv-cache`, also used for the subsequent uv commands.
- `uv run fedcourts query --court scotus --citation '583 U.S. 281' --limit 2` returned no rows for *Jennings v. Rodriguez* and reported sparse citation coverage. `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
- `uv run fedcourts query --court scotus --disposition gvr --decided-before 2026 --limit 3` returned *Casarez*, *Roybal*, and *Harrington*. These illustrate the GVR label but provide no issue-specific comparison. `ranged corpus reads: 29 GET(s), 7471104 byte(s)`
- `uv run fedcourts query --court scotus --docket-number 26-572 --limit 1` returned *Padula v. Cirrus Rojas*, with one distribution and no disposition. `ranged corpus reads: 17 GET(s), 4456448 byte(s)`
- `uv run fedcourts query --court scotus --docket-number 26-104 --limit 1` returned the October 1 grant in *Rhoney v. Barbosa da Cunha*. `ranged corpus reads: 0 GET(s), 0 byte(s)`
- Consulted the modern cert, circuit, relist, CVSG, amicus and federal-band tables in `metrics/statpack.md`. Checked the versioned Term rows in `metrics/statpack.json` and pooled the prior sal-v9 federal rows.

## CourtListener MCP

- `search` for opinions, court `ca1`, docket `25-2152`, filed before 2026-11-13, returned the August 13 opinion in *Guerrero Orellana v. Moniz*.
- `read_document` for opinion 11415407 returned the combined majority and dissent. Read the statutory holding, class posture, prior circuit decisions and dissent. [First Circuit opinion](https://www.courtlistener.com/opinion/10947821/guerrero-orellana-v-moniz/)

## Official filing and docket lookups

- The guessed DOJ brief page `/osg/brief/mullin-v-guerrero-orellana` returned HTTP 404. The DOJ brief index loaded and surfaced two other detention petitions. A caption search for Guerrero Orellana returned no results. A search for 26-630 was fetched twice because the first text extraction produced no output. The second confirmed no result. [DOJ brief index](https://www.justice.gov/osg/supreme-court-briefs)
- Opened DOJ’s brief pages for *Padula* and *Quinones* and read the linked petitions with `uv run fedcourts pdf-text` using in-memory file descriptors. Both present the § 1225(b)(2)(A) question. Read the *Padula* PDF a second time to extract its reasons and conclusion, which request a hold for No. 26-104. [Padula posting](https://www.justice.gov/osg/brief/padula-v-cirrus-rojas) · [Quinones posting](https://www.justice.gov/osg/brief/quinones-v-rodriguez-vazquez)
- Opened the official docket for *Rhoney*, No. 26-104, to verify the grant and merits briefing schedule. Reopened it to locate the questions-presented link and read the one-page PDF with `uv run fedcourts pdf-text`. [Docket](https://www.supremecourt.gov/docket/docketfiles/html/public/26-104.html) · [Granted question](https://www.supremecourt.gov/qp/26-00104qp.pdf)
