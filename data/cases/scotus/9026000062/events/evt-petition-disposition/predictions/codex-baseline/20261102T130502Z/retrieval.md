# Retrieval record

## Provisioned and committed materials

Read the event definition, `record/snapshots/2026-11-02.json`, `context.json`, `documents.json`, questions presented, petition, combined oppositions, reply, relevant appendix passages, and `same-question.json`. Consulted the prediction contract and output schemas, and the committed `metrics/statpack.md`, especially the paid-segment relist, CVSG, amicus, and sal-v6 reached-band tables. The frozen anchor in context, not the current Term's rate, governs the prediction.

## Corpus CLI calls

1. `UV_NO_CACHE=1 uv run --no-sync fedcourts query --help` — read supported filters and retrieval semantics. Repeated the help command with `COLUMNS=160` and displayed its options section to avoid abbreviated flag descriptions. Neither help call performed corpus retrieval or printed a transfer line.
2. `UV_NO_CACHE=1 uv run --no-sync fedcourts query --court scotus --citation '591 U.S. 197' --decided-before 2026 --limit 1` — attempted a metadata lookup of Seila Law, a structural-accountability precedent cited by the petition. Returned no case and warned that only 200 SCOTUS rows in scope carried reporter citations, making an empty citation lookup a coverage limitation rather than evidence of no precedent. No opinion body was retrieved.

   `ranged corpus reads: 10 GET(s), 2621440 byte(s)`

3. `UV_NO_CACHE=1 uv run --no-sync fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026 --limit 3` — returned metadata for U.S. DOGE Service v. United States District Court (25-1103), Corey Duran Berry v. United States (25-7026), and Todd Blanche v. Izuchukwu Ozurumba (25-1343), each recording an October 13, 2026 cert grant. None had an opinion body or a topic summary establishing relevance to master-account access. No substantive analogy or probability adjustment was made from this grant-selected sample. The year filter applies the corpus's docket-Term clock; these other petitions were docketed in Term 2025 and their grant dates precede the prediction snapshot.

   `ranged corpus reads: 27 GET(s), 7077888 byte(s)`

No `open-events` call and no query about this petition's disposition or later history was made.

## Attempted web retrieval

The following `web.run` calls produced no visible results or page contents. They yielded no citations, factual additions, or outcome information used in the forecast:

1. One search call containing two queries: `site.uscode.house.gov 12 USC 248a c 2 all Federal Reserve bank services available nonmember` and `site.supremecourt.gov ctrules 2023 Rule 10 compelling reasons conflict`. Intended to verify the general statutory text and certiorari standard, not this case's status.
2. Opened `https://www.supremecourt.gov/filingandrules/rules_guidance.aspx` to seek official procedural rules. No visible content returned.
3. Opened `https://uscode.house.gov/view.xhtml?edition=prelim&num=0&req=granuleid%3AUSC-prelim-title12-section248a` to seek the official statute. No visible content returned.

No live Supreme Court docket page, case-outcome search, or CourtListener MCP lookup was attempted. The forecast instead uses the pre-decision filings and lower-court material staged in the record.

## Operational calls

The first required `uv run fedcourts paths --court scotus --docket 9026000062 --event evt-petition-disposition --role predictor` failed because uv's default cache location was read-only. Retrying with `UV_NO_CACHE=1 uv run --no-sync fedcourts paths --court scotus --docket 9026000062 --event evt-petition-disposition --role predictor` succeeded. No package installation was attempted. Paths, schema inspection, and final validation are local operations, not additional evidence retrieval.
