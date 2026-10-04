# Retrieval record

All case-specific substantive material consulted concerns the record at or before the October 1, 2026 grant. No Supreme Court merits outcome, subsequent-history search, other predictor's output, or labeling-measurement artifact was read.

## Local sources and utilities

- Read the contract, output schemas, provisioned event/context, and snapshot `2026-10-02.json`. The case-level record contains no documents directory.
- Read only the merits section and introductory metadata of `metrics/statpack.md`; inspected top-level keys of `metrics/statpack.json` for vintage information. Computed the prior-Term pool from the merits rows: 377 disturbed / 540 parsed.
- Read `src/fedcourtsai/supremecourt.py`'s `october_term_year` function to apply the registered grant-Term boundary rather than substitute a first-Monday calculation.
- Ran `uv run fedcourts paths --court scotus --docket 9026000104 --event evt-order-judgment --role predictor`. The first attempt failed because the default cache was read-only; rerunning with a writable temporary cache succeeded. No outcome path was opened.
- No `fedcourts query`, `open-events`, live corpus read, or comparable-case corpus lookup was performed. Consequently there is no ranged-corpus transfer line to report.

## Web tool attempts

The following searches/opens returned no usable results or document text:

1. Search: `"Rhoney" "Cunha" petition certiorari` and `site.supremecourt.gov "26-104" questions presented`.
2. Search: `"Barbosa da Cunha" "Rhoney"`; `"Cunha" "25-3141"`; `"Rhoney" "certiorari"`.
3. Open the official QP PDF: `https://www.supremecourt.gov/qp/26-00104qp.pdf`.
4. Search: `site.supremecourt.gov about biographies current members` and `site.uscode.house.gov "1225" "seeking admission"`.
5. Open the lower-court PDF: `https://ww3.ca2.uscourts.gov/decisions/OPN/25-3141_complete_opn.pdf`.

## CourtListener MCP

1. Opinion search, case name `Cunha`, court `ca2`, filed after `2026-04-27` and before `2026-04-29`, limit 5. Returned *Cunha v. Freden*, No. 25-3141, April 28, 2026, cluster 10848967, opinion 11316346, with its official Second Circuit PDF address. This is the judgment below, not the Supreme Court judgment being forecast.
2. `read_document(opinion_id=11316346)`: no document text available.
3. Opinion endpoint item 11316346, fields `plain_text`, `html`, `html_lawbox`, `html_columbia`, `html_with_citations`, `download_url`: all text fields empty; confirmed the official download address.
4. Opinion search, case name `Buenrostro-Mendez`, court `ca5`, filed before `2026-10-02`, limit 2: no results.
5. Opinion search, citation `166 F.4th 494`, limit 2: no results. I did not inspect that opinion; discussion of it is attributed to the Second Circuit's pre-grant opinion.

## Direct official sources

- `https://www.supremecourt.gov/qp/26-00104qp.pdf`: one-page QP sheet; identifies the statutory mandatory-detention question, lower citation 175 F.4th 61, docket 25-3141, and October 1, 2026 cert grant. Successful HTTP retrieval and in-memory extraction with `pypdf`. The grant is already in the provisioned record, not the forecast outcome.
- `https://ww3.ca2.uscourts.gov/decisions/OPN/25-3141_complete_opn.pdf`: 69-page combined April 28, 2026 lower-court opinion. Successfully retrieved and extracted in memory. The full-text terminal output was truncated, so this was not an uninterrupted full read. I separately requested PDF pp. 11–21 (also partially truncated), then pp. 14–17 (fully displayed). Readable opening pages and the end of the separate concurrence supplied additional context. Reasoning cites only material actually displayed. No later appellate history was requested.
- Initial `curl` requests piped into `pdftotext` for these two PDFs failed because `pdftotext` was absent. The successful method used the project's installed `httpx` and `pypdf`; no downloaded source file was written.
- `https://www.supremecourt.gov/about/biographies.aspx`: official current-members page, retrieved directly and checked for the nine named Justices. An initial paragraph-based extraction returned no entries; a raw text preview was unhelpful; the final extraction stripped script/style content and located each Justice by name. Used only to confirm roster, not infer votes.

Direct requests were to court-owned public document hosts, not to CourtListener REST endpoints. No credentials were sought or used for these requests. No outcome-revealing Supreme Court material surfaced.
