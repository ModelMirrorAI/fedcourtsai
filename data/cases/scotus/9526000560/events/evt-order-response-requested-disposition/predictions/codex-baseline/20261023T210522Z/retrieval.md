# Retrieval record

## Local inputs and base rates

- Read the cell contract, schemas, event definition, `record/context.json`, `record/snapshots/2026-10-23.json`, `record/documents/documents.json`, and `record/documents/application.txt`.
- Read the committed `metrics/statpack.md` interim-docket section. Computed the strictly-prior 2016–2025 substantive resolved pool as 51 grants / 547 resolutions. No corpus query or open-events lookup was made; there are no ranged-read transfer lines to report.
- Ran `fedcourts paths` for the specified court, docket, event, and predictor role. The initial invocation encountered a read-only default uv cache; the retry used a cache under `/tmp` and succeeded. No outcome file was opened.

## CourtListener MCP

1. `search(type="o", citation="511 U.S. 462", num_results=1)`: found Dalton v. Specter, decided May 23, 1994; lead opinion id 9527076.
2. `search_document(opinion_id=9527076, query="statutory authority", snippet_size=550)`: read the discussion distinguishing constitutional violations from excess statutory authority, principally 511 U.S. at 472–474. This supported the jurisdictional analogy, not knowledge of this application's result.
3. `search(type="o", citation="588 U.S. 930", num_results=1, fields=[caseName,citation,dateFiled,opinions,absolute_url])`: no results for the prior Trump v. Sierra Club order.
4. `search(type="o", case_name="Trump v. Sierra Club", filed_after="2019-07-25", filed_before="2019-07-28", num_results=1, fields=[caseName,citation,dateFiled,opinions,absolute_url])`: no results. Did not infer that the cited order does not exist.
5. `search(type="o", citation="404 F. Supp. 3d 218", num_results=1, fields=[caseName,citation,dateFiled,opinions,absolute_url])`: no results for the earlier waiver litigation. Relied only on the provisioned application's account, with that limitation disclosed.

## Web tools

- Search queries: `site.supremecourt.gov Dalton Specter 511 462 1994 constitutional statutory authority`; `site.ca9.uscourts.gov 915 F.3d 1213 Border Infrastructure high illegal entry 2019`.
- A further search query: `Dalton Specter 511 462 472 constitutional statutory claims Supreme Court`.
- Attempted to open the official Supreme Court PDF path for the 2019 order in application 19A60 (`/opinions/18pdf/19a60_o75p.pdf`).
- These web calls returned no usable content in the session. They contributed no evidence. All requests concerned earlier authorities, not this case's current docket or disposition.

No search sought this application's outcome, subsequent history, another cell's output, or labeling-measurement artifacts.
