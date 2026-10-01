# Retrieval beyond the provisioned inputs

## Local context

- Read the committed `metrics/statpack.md` merits section and `metrics/statpack.json` merits rows. Used no cert-band anchor. A heading/row-location command also surfaced unrelated cert/interim table lines; they were not used in this merits forecast.
- Inspected `fedcourtsai.supremecourt.october_term_year` to settle the October 1 grant-Term boundary, and executed an in-memory sum of the statpack's 2016–2025 rows: grant Term 2026; 377 disturbed, 540 parsed, 589 grants, 66 excluded.
- Ran `git log -1 --format='%h %cI' -- metrics/statpack.md`: `808f812e9 2026-09-28T12:02:50Z`. This dates the committed file, not the underlying corpus refresh.
- Read the prompt, applicable instructions, artifact schemas, and path/serialization helpers for the output contract. Ran `uv run fedcourts paths --court scotus --docket 73281619 --event evt-order-judgment --role predictor`; the first attempt failed because the default cache was read-only, and retrying with a writable temporary cache succeeded. No outcome file was opened.
- No `fedcourts query`, `open-events`, corpus pull, or case-history lookup was performed. Consequently there are no ranged-corpus-read transfer lines to report.

## General-law web attempts

One batched search requested:

1. `site.supremecourt.gov opinions 2014 Holt Hobbs 13-6827 pdf`
2. `site.uscode.house.gov 42 2000cc-5 religious exercise building`
3. `site.supremecourt.gov about biographies current members`

An additional open requested the official U.S. Code Chapter 21C page at `https://uscode.house.gov/view.xhtml?edition=prelim&path=%2Fprelim%40title42%2Fchapter21C`.

These web calls produced no usable visible results or page text. They supplied no evidence and did not confirm the roster. The vote forecast assumes participation by the nine named Justices; the provisioned docket gives no contrary participation information. None of these requests sought this case's outcome.

## CourtListener MCP

1. `search(type="o", citation="574 U.S. 352", num_results=1, fields=["caseName", "dateFiled", "citation", "opinions", "absolute_url"])`. The returned first result was Henderson v. Schneckloth (1957), not Holt. It was disregarded; no further results from that query were read.
2. `search(type="o", case_name="Holt v. Hobbs", court="scotus", filed_after="2015-01-19", filed_before="2015-01-21", num_results=3, fields=["caseName", "dateFiled", "citation", "opinions", "absolute_url"])`. Returned Holt v. Hobbs, January 20, 2015, cluster 2771249, including lead-opinion ID 9805717.
3. `search_document(opinion_id=9805717, query="other forms", snippet_size=1700)`. Read the single match discussing the particular religious exercise, alternative religious practices, and RLUIPA's protection of exercise not compelled by doctrine. This confirmed the prior-law passage at 574 U.S. 361–62; no target-case material was requested or returned.

The additional retrieval did not surface the target case's merits outcome or reasoning.
