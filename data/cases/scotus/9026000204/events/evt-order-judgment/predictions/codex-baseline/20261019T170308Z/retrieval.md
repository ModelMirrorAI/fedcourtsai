# Retrieval record

## Local inputs and reference artifacts

- Read the provisioned event, context, October 19, 2026 snapshot, document manifest, questions presented, and portions of the petition, opposition, and cert reply identified in `reasoning.md`.
- Read the task contract and output schemas. Consulted the path and serialization helpers to place and serialize only this cell's outputs.
- Ran `uv run fedcourts paths --court scotus --docket 9026000204 --event evt-order-judgment --role predictor`. The first attempt failed because the default cache location was read-only; a retry with a temporary writable cache succeeded. No outcome file was opened.
- Read the committed `metrics/statpack.md` merits section and `metrics/statpack.json` merits rows, and computed the 2016–2025 window with a local Python sum. Inspected the pack's JSON keys and coverage metadata for vintage information; inspected its last commit timestamp. No corpus lookup was made.
- No `fedcourts query` or `open-events` calls; consequently no ranged-corpus transfer lines were emitted.

## Web attempts

The following `web.run` requests returned no usable results or page content. No evidence or outcome information was taken from them:

1. Search: `United States v Dewitt 76 US 41 1869 distilling liquors taxed articles`.
2. Search: `Felsenheld United States 186 US 126 1902 tobacco packages`.
3. Search: `site.supremecourt.gov about biographies current members Court`.
4. Search: `site.supremecourt.gov opinions 09pdf 08-1224 Comstock`.
5. Open: the Library of Congress United States Reports PDF for volume 186, page 126 (`tile.loc.gov`, object `usrep186126.pdf`).

These requests sought general legal context and bench identification, not McNutt's disposition or subsequent history. Bench composition was not independently confirmed by a usable web response.

## CourtListener MCP

1. `search(type="o", citation="76 U.S. 41", num_results=1)`. Returned *United States v. Clintwood Elkhorn Mining Co.*, cluster/opinion 2959731, rather than the intended case; not used in the forecast. No opinion body was opened.
2. `search(type="o", case_name="United States v. Dewitt", court="scotus", filed_before="1871-01-01", num_results=2, fields=["caseName", "citation", "dateFiled", "opinions", "cluster_id"])`. Identified *United States v. Dewitt*, 76 U.S. 41, opinion 88133.
3. `search(type="o", case_name="Felsenheld", court="scotus", filed_before="1903-01-01", num_results=1, fields=["caseName", "citation", "dateFiled", "opinions", "cluster_id"])`. Identified *Felsenheld v. United States*, 186 U.S. 126 (1902), opinion 95673.
4. `search_document(opinion_id=88133, query="distilling", snippet_size=1100)`. Read the passage at page 44 distinguishing regulations of taxed articles from an indirect attempt to increase revenue by prohibiting another product.
5. `search_document(opinion_id=95673, query="reasonable", snippet_size=1200)`. Read passages at pages 132–33 supporting reasonable categorical requirements for packages of taxable goods.

No target-case search, current docket retrieval, realized-outcome file, another predictor's output, or labeling-measurement artifact was consulted.
