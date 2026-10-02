# Retrieval record

No retrieval sought this case's merits disposition, subsequent history, post-grant advocacy, other predictors' outputs, or evaluation materials.

## Local context beyond provisioned case inputs

- Read the committed merits section of metrics/statpack.md and the corresponding merits Term counts in metrics/statpack.json. Calculated the 2016–2025 window: 377 disturbed, 540 parsed, 589 granted, 66 separately excluded. No live corpus query or open-events lookup; there is no ranged-corpus-read stderr line to report.
- Inspected the date-to-Term rule in src/fedcourtsai/supremecourt.py, the grant-Term selection in src/fedcourtsai/cli.py, and the window/floor rule in src/fedcourtsai/pipeline/base_rates.py to avoid substituting the docket Term for the grant Term. No code was changed.
- Read the task contract and output schemas. Ran `uv run fedcourts paths --court scotus --docket 73500251 --event evt-order-judgment --role predictor`; its first attempt failed because the default uv cache location was read-only. The same command with the cache directed to /tmp/uv-cache succeeded. It did not read an outcome.

## Web tool attempts

The following web.run requests returned no usable result text:

1. Searches: `site.supremecourt.gov opinions 2016 Howell Howell 15-1031 pdf`; `site.uscode.house.gov 10 1408 court order property settlement`; `site.supremecourt.gov about justices current members`.
2. Open of the official historical Howell opinion:

```text
https://www.supremecourt.gov/opinions/16pdf/15-1031_hejm.pdf
```

No substantive inference rests on these empty responses.

## CourtListener MCP

1. `search(type="o", citation="490 U.S. 581", num_results=1)`: returned an unrelated Dean result; disregarded.
2. `search(type="o", case_name="Mansell v. Mansell", court="scotus", num_results=3)`: returned a loose name match and historical cert orders, not the requested merits opinion; not used as substantive support.
3. `search(type="o", q='caseName:"Mansell v. Mansell" AND dateFiled:[1989-01-01 TO 1989-12-31]', court="scotus", num_results=3)`: located Mansell, 490 U.S. 581, May 30, 1989, combined opinion 112267.
4. `search(type="o", q='caseName:"Howell v. Howell" AND dateFiled:[2017-05-01 TO 2017-05-31]', court="scotus", num_results=2)`: located Howell, 581 U.S. 214, May 15, 2017, combined opinion 4168364 and a duplicate representation.
5. `read_document(opinion_id=4168364, chunk_index=[0,1,2], chunk_size=7000)`: read returned portions of Howell's syllabus and opinion; tool display was partly truncated.
6. `search_document(opinion_id=[4168364,112267], query="res judicata", snippet_size=1200)`: no Howell match; read Mansell footnote 5 on state-law finality and adjacent footnote 6.
7. `search_document(opinion_id=4168364, query="THOMAS", snippet_size=1100)`: read the participating lineup and Thomas's separate opinion, with adjacent passages concerning the judgment and support distinction.

These were general precedents from 1989 and 2017, not this case's outcome. No direct CourtListener REST request was made.

## Direct official-page retrieval

Used curl with a 20-second timeout, stripped HTML, and filtered for the nine Justice names on the Court's biographies page. This supplied the current roster only:

```text
https://www.supremecourt.gov/about/biographies.aspx
```

Attempted a similarly filtered official statutory read for court-order and waiver language; the command returned no matching passage, so it did not independently verify the provision:

```text
https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title10-section1408&num=0&edition=prelim
```

All retrieval occurred October 2, 2026. Provisioned filings remain the source for the case-specific statutory arguments and lower-court record.
