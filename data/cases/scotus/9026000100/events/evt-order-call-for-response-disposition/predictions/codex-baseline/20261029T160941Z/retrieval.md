# Retrieval record

No search sought this petition's disposition, subsequent history, later docket
entries, or another cell's output. The only target-case material read was the
provisioned record. No material under `data/qp-topics/` was read.

## Local reference and CLI reads

- Read `AGENTS.md`, `.github/prompts/predict.md`, and the prediction and tooling
  schemas. Read `metrics/statpack.md` and the relevant `terms[].segments[]`
  fields of `metrics/statpack.json`; calculated the 2017-2025 sal-v4 baseline
  risk-set pool as 660/12,913. Read path, identifier, and serialization helper
  definitions to respect output conventions. These were local reads, not live
  corpus queries.
- Attempted `uv run fedcourts paths --court scotus --docket 9026000100 --event
  evt-order-call-for-response-disposition --role predictor` and
  `uv run fedcourts query --help` initially without a cache override. Both failed
  before running because the default uv cache was read-only. Retried with
  `UV_CACHE_DIR=/tmp/uv-cache`; both succeeded. The paths command was only a path
  resolver and did not open an outcome. Repeated the query help with
  `COLUMNS=160` to read its structured filters. Also read
  `uv run fedcourts validate --help` using the same cache override.

## Corpus queries

1. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition granted --decided-before 2026 --limit 3`

   `ranged corpus reads: 28 GET(s), 7340032 byte(s)`

   Returned three grant records, dockets 25-1103, 25-7026, and 25-1343. They were
   broad modern-grant examples, not close substantive analogues; no opinion
   bodies were requested and their particular outcomes did not drive the number.
   The term-year filter can admit a prior-Term docket resolved in 2026. This cell
   is forward, not replay; none of the rows was the target case.

2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '605 U.S. 303' --decided-before 2026 --limit 1`

   `ranged corpus reads: 7 GET(s), 1835008 byte(s)`

   Returned no rows and a warning that only 200 SCOTUS rows in scope carry reporter
   citations, so a citation miss is more likely missing coverage than no precedent.
   Did not repeat the sparse filter or infer that Ames does not exist.

## CourtListener MCP

- `search(type="o", case_name="Hittle v. City of Stockton", court="scotus",
  filed_before="2026-08-14", num_results=3)` failed with HTTP 429: the server's
  daily rate limit was exhausted. No opinion text was received. No CourtListener
  REST fallback was attempted.

## Web tool calls

All searches concerned earlier general legal context, never Cross's own outcome.

1. Search queries: `site.supremecourt.gov opinions 2024 Hittle Stockton Thomas
   Gorsuch denial certiorari McDonnell Douglas February 24 2025` and
   `site.supremecourt.gov opinions Ames Ohio Department Youth Services 2025 Thomas
   McDonnell Douglas summary judgment`. This initial tool call returned no usable
   visible result. The February date was a search term, not a verified decision
   date; the official opinion later verified March 10, 2025.
2. Attempted open of the official Hittle PDF below; this initial call returned
   no usable visible text.
3. Attempted find for `In an appropriate case` in the official Ames PDF below;
   this initial call returned no usable visible text.
4. Search: `site.supremecourt.gov "Ames" "23-1039" "2025"`. No usable visible
   text was available from this web-tool attempt either.
5. Requested both official PDFs through the web tool; no usable visible text
   was available from these attempts:
   - `https://www.supremecourt.gov/opinions/24pdf/23-1039_c0n2.pdf`
     Ames, decided June 5, 2025: majority rejects the majority-group heightened
     prima-facie requirement; Thomas concurrence joined by Gorsuch criticizes
     the broader framework.
   - `https://www.supremecourt.gov/opinions/24pdf/24-427_l5gm.pdf`
     Hittle, decided March 10, 2025: denial of certiorari, with Thomas dissenting,
     joined by Gorsuch, on the proof-framework issue.
6. Requested Ames again to examine its limited holding and concurrence. No usable
   visible text was available from that web-tool attempt. No third-party result
   was used as a substitute for either opinion.

## Independent official-source verification

Because the web-tool attempts did not provide usable visible text, verified both
official PDF addresses above through the shell. Initial `curl --fail --silent
--show-error <official-PDF-address> | pdftotext - -` attempts failed because
`pdftotext` was not installed; curl reported a broken output pipe. Checked that
the existing environment provided `httpx` and `pypdf`, without installing or
modifying dependencies. Then used `UV_CACHE_DIR=/tmp/uv-cache uv run python`
to GET each PDF with `httpx`, parse its bytes in memory with `pypdf.PdfReader`,
and inspect selected pages. Both returned HTTP 200. Ames had 25 PDF pages;
read its syllabus, the majority's concluding page, and the concurrence's last
page. Hittle had nine PDF pages; read its first and last pages. Those successful
reads verified the dates and limited holdings summarized above, Hittle's denial
and named dissenters, and the invitation in the Ames concurrence. This was an
official Supreme Court source check for earlier general legal context, not a
CourtListener REST fallback or a search for this petition's outcome.

No historical opinion body from these sources was reproduced in the output.
