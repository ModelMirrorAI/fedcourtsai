# Retrieval log

## Local inputs and reference artifacts

- Read the supplied contract, output schemas, event, context, snapshot, document manifest, questions presented, and selected sections of the petition, BIO, and both merits briefs. These are provisioned inputs, not external retrieval.
- Read the committed merits section in `metrics/statpack.md` and corresponding `merits` data in `metrics/statpack.json`. A heading-location search incidentally displayed cert/interim rows; none of those rates was used. Computed the eligible 2015–2024 pool locally: observed Terms 2017–2024, 360 disturbed, 516 parsed, 539 granted, 56 excluded.
- Ran `uv run fedcourts paths --court scotus --docket 73274866 --event evt-brief-judgment --role predictor`. The initial attempt failed because the default cache was read-only; retried successfully with a temporary cache. This resolved paths, not case facts. No outcome file was read.
- No `fedcourts query` or `fedcourts open-events` call was made. There are no ranged-corpus transfer lines to report.

## Web searches

The following queries were submitted in three `web.run` calls. All returned no usable result content; no web page was opened and no target-case outcome was surfaced.

1. `site.supremecourt.gov "Cisco" "2026" "Doe" opinion`
2. `site.supremecourt.gov "Medina" "2025" "Cannon"`
3. `"Alexander v. Sandoval" "532" "275"`
4. `"Jackson v. Birmingham" "544" "167"`
5. `"Cisco Systems" "Doe I" "2026" Supreme Court`
6. `site.supremecourt.gov opinions "Medina" "24-316"`
7. `site.supremecourt.gov "Jackson" "02-1672"`

The Medina search using 24-316 did not return anything; the successful CourtListener lookup identified the actual docket as 23-1275. No inference rests on that unsuccessful query.

## CourtListener MCP

1. `search(type="o", case_name="Medina v. Planned Parenthood", court="scotus", num_results=2)`. Returned the June 26, 2025 decision and duplicate report versions; used opinion 11084231.
2. `search_document(opinion_id=11084231, query="Cannon", snippet_size=1500)`. Read the majority's discussion of the ratified holding and abandoned methodology; used as general doctrinal context.
3. `search(type="o", case_name="Cisco Systems", court="scotus", filed_after="2026-01-01", num_results=3, fields=["caseName", "dateFiled", "citation", "opinions", "absolute_url"])`. Returned the June 23, 2026 decision, opinion 11346054.
4. `read_document(opinion_id=11346054, chunk_index=0, chunk_size=13500)`. Read the opening/syllabus portion describing the ATS and TVPA issues and outcome. This is a prior case, not the predicted case.
5. `search_document(opinion_id=11346054, query="joined", snippet_size=450)`. Checked the majority coalition and separate-writing alignments.
6. `search_document(opinion_id=11346054, query="virtually", snippet_size=1600)`. Checked the opinion's own separation-of-powers discussion and accompanying dissent excerpt.

No target-case live docket lookup, disposition search, subsequent-history search, or opinion retrieval occurred. All external substantive material used concerned general precedents predating the provisioned August 18, 2026 baseline.
