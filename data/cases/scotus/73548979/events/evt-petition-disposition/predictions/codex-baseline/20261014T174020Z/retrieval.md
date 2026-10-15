# Retrieval record

## Provisioned baseline

Read the case-level October 14, 2026 snapshot and context, the event definition, document manifest, QPs, and relevant argument portions of the petition, BIO, and reply. These are baseline inputs, not external retrieval. Did not read outcomes, other predictions, or anything under `data/qp-topics/`.

## Committed reference material

- Read `metrics/statpack.md`: modern-cert disposition and originating-circuit sections, paid-segment relist and CVSG cuts, and the sal-v4 prior-Term reached-band table.
- Read `metrics/statpack.json` to obtain exact prior-Term elevated risk-set rates and denominators. Executed a local calculation over the displayed 2017–2024 rows: sum of rate × denominator = 484; sum of denominator = 2,810; ratio = 0.17224199288256228. No case-level prior was retrieved.
- Ran `git log -1 --format='%h %cI' -- metrics/statpack.md`; result: `cf9ae960e 2026-10-13T19:17:46Z`. This dates the committed artifact, not the underlying corpus's newest pull.
- Read the prediction and tooling schemas and task instructions for the output contract.

## Web-tool attempts

1. `web.run` open of the exact September 21 supplemental-brief PDF URL already present in the snapshot. The tool returned no usable content.
2. `web.run` searches for `site.supremecourt.gov opinions 2022 22-96 financial oversight Centro sovereign immunity Thomas` and `site.supremecourt.gov "25-1426" "Supplemental" "September"`. No results or snippets were returned. These were targeted precedent/filing lookups, not a request for this petition's outcome.

## Official supplemental filing

Retrieved only the known, dated filing at:

`https://www.supremecourt.gov/DocketPDF/25/25-1426/424994/20260921113103647_25-1426%20Supplemental%20Brief.pdf`

An initial `curl -fLsS --max-time 40 <that URL> | pdftotext - -` attempt failed because `pdftotext` was unavailable; curl consequently reported a broken output destination. No text was obtained in that attempt.

Retried using `uv run python` with `httpx.get(url, timeout=40, follow_redirects=True)`, then `PdfReader(io.BytesIO(response.content))` and each page's `extract_text()`. HTTP 200; read the cover and both substantive pages in memory, without saving a document. The September 21 filing reports a September 15 USPTO speech and requests a grant or CVSG. Did not follow the speech link or retrieve the current docket. No decision material was returned.

## CourtListener MCP

1. `search(type="o", citation="598 U.S. 339", num_results=3, fields=["id", "caseName", "dateFiled", "citation", "opinions", "absolute_url"])`: returned two records of the May 11, 2023 Financial Oversight decision, plus an unrelated numerical citation match. Used the 2023 case only, opinion ID 9393811. The server noted the requested `id` field was not available at the result level; the nested opinion ID was present.
2. `search_document(opinion_id=9393811, query="singularly", snippet_size=1800)`: no literal match.
3. `search_document(opinion_id=9393811, query="immunity", snippet_size=450)`: snippets confirming the assumption-without-decision posture and abrogation issue.
4. `read_document(opinion_id=9393811, chunk_index=[2,5], chunk_size=8000)`: portions of the majority's framing and Thomas's dissent. Used only the general legal context predating the present petition.

## Corpus commands and operational notes

No `fedcourts query` or `fedcourts open-events` call was made; therefore no `ranged corpus reads` line was emitted. No live corpus freshness claim is made.

Ran `uv run fedcourts paths --court scotus --docket 73548979 --event evt-petition-disposition --role predictor`. The first invocation could not initialize the default read-only cache; retrying with `UV_CACHE_DIR=/tmp/uv-cache` succeeded. This resolved paths, not historical case data. The same writable cache setting was used for local arithmetic and validation.
