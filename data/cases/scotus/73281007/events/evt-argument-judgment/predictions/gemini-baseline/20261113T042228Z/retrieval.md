# Retrieval Log — `scotus/73281007` · `evt-argument-judgment`

## 1. Local `fedcourts` CLI Lookups

1. `uv run fedcourts paths --court "scotus" --docket "73281007" --event "evt-argument-judgment" --role predictor` and `uv run fedcourts query --help`
   - Returned case/event/corpus paths (`case_id: scotus/73281007`, `corpus: corpus/corpus.db`, `event: data/cases/scotus/73281007/events/evt-argument-judgment/event.yaml`) and CLI flag documentation.
2. `uv run fedcourts query --court scotus --citation "603 U.S. 109" --limit 10`
   - `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Returned 0 rows, with note explaining that only 195 SCOTUS rows carry own parallel citations and the column stores a case's own citations rather than citing-case edges.
3. `uv run fedcourts query --court scotus --docket-number "25-406"`
   - `ranged corpus reads: 21 GET(s), 5505024 byte(s)`
   - Returned 1 row: `scotus/73221533` (*Federal Communications Commission, et al. v. AT&T, Inc.*, `merits_decided: "2026-06-04"`, `merits_judgment: "reversed"`).
4. `uv run fedcourts query --court scotus --originating-court ca3 --disposition granted --limit 50`
   - Refused (`Exit Code: 2`, `No such option: --originating-court`).
5. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 25`
   - `ranged corpus reads: 50 GET(s), 13041664 byte(s)`
   - Returned 25 recent 2020s granted SCOTUS rows (pending OT2026 grants and resolved interim applications).

## 2. CourtListener MCP Lookups

All CourtListener lookups were strictly limited to external precedents cited in the provisioned merits briefs and oral argument transcript (never querying `Sun Valley Orchards` or docket `25-966` / `73281007`):

1. `courtlistener.search` (`type="o"`, `court="scotus"`, `case_name="FCC v. AT&T"`, `filed_after="2026-01-01"`, `num_results=5`, `fields=["caseName", "citation", "dateFiled", "cluster_id", "opinions", "syllabus"]`)
   - Returned 1 result: *FCC v. AT&T*, `cluster_id: 10870061`, `opinion_id: 11337518`, `dateFiled: "2026-06-04"`.
2. `courtlistener.read_document` (`opinion_id=11337518`, `chunk_index=[0, 1, 2]`, `chunk_size=8000`)
   - Returned chunks 0–2 of *FCC v. AT&T* (slip opinion syllabus and opening pages).
3. `courtlistener.search` (`type="o"`, `court="scotus"`, `case_name="Sripetch v. SEC"`, `filed_after="2026-01-01"`, `num_results=5`, `fields=["caseName", "citation", "dateFiled", "cluster_id", "opinions", "syllabus"]`)
   - Returned 1 result: *Sripetch v. SEC*, `cluster_id: 10870059`, `opinion_id: 11337516`, `dateFiled: "2026-06-04"`.
4. `courtlistener.read_document` (`opinion_id=11337516`, `chunk_index=0`, `chunk_size=8000`)
   - Returned chunk 0 (syllabus) of *Sripetch v. SEC* (disgorgement / pecuniary harm).
5. `courtlistener.search_document` (`opinion_id=11337518`, `query="impose"`, `snippet_size=450`)
   - Returned 10 snippets from *FCC v. AT&T* discussing penalty imposition and 47 U.S.C. § 504(a).
6. `courtlistener.search` (`type="o"`, `court="scotus"`, `case_name="Trump v. Slaughter"`, `filed_after="2026-01-01"`, `num_results=5`, `fields=["caseName", "citation", "dateFiled", "cluster_id", "opinions", "syllabus"]`)
   - Returned 1 result: *Trump v. Slaughter*, `cluster_id: 10881681`, `dateFiled: "2026-06-29"`.
7. `courtlistener.read_document` (`opinion_id=11337518`, `chunk_index=[0, 1]`, `chunk_size=3500`)
   - Returned smaller unmasked chunks 0–1 of the *FCC v. AT&T* syllabus.
8. `courtlistener.search_document` (`opinion_id=11337518`, `query="joined"`, `snippet_size=350`)
   - Returned 1 snippet confirming the 8–1 vote lineup in *FCC v. AT&T* (Roberts, C.J., for an 8-Justice majority; Thomas, J., dissenting).
9. `courtlistener.read_document` (`opinion_id=11337518`, `chunk_index=[2, 3, 4]`, `chunk_size=3500`)
   - Returned chunks 2–4 of the *FCC v. AT&T* syllabus contrasting 47 U.S.C. § 504(a)'s trial de novo safeguard with *SEC v. Jarkesy*.

## 3. Web Searches

None attempted.
