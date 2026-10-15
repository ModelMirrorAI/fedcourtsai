# Retrieval record

## Provisioned inputs

- Read the event definition, `record/context.json`, and `record/snapshots/2026-10-14.json` for this cell.
- Read `record/documents/documents.json`, `questions-presented.txt`, and relevant petition sections, including the lower-court opinions in its appendix. No BIO was present.

## Local context beyond the provisioned record

- Read the prediction prompt, AGENTS.md, and the prediction, tooling, and flags schemas.
- Read the modern-cert, originating-circuit, paid relist, paid CVSG, and sal-v4 per-Term band sections of `metrics/statpack.md`.
- Read `metrics/statpack.json` for exact baseline reached rates and weighted denominators; pooled Terms 2017–2025 only. Result: 643 weighted grants / 12,877 weighted resolved = 0.04993399083637493. The 2026 row was not used as an anchor.
- Ran `uv run fedcourts paths --court scotus --docket 9026000223 --event evt-petition-disposition --role predictor`. The first attempt could not initialize the default read-only cache; reran successfully with a writable temporary cache. Read the repository path and serialization helpers for output handling.
- No `fedcourts query` or `open-events` lookup was made; no ranged corpus transfer line was produced.

## Web attempts

These general-authority requests returned empty tool responses: no snippets, documents, or usable source references. They supplied no substantive information.

1. Search queries: `site.loc.gov "Milkovich v. Lorain" "497"` and `site.supremecourt.gov "Rule 10" "misapplication"`.
2. Open attempted: `https://www.supremecourt.gov/filingandrules/2023RulesoftheCourt.pdf`.
3. Open attempted: `https://www.supremecourt.gov/filingandrules/rules_guidance.aspx`.

## CourtListener MCP

1. `search(type="o", citation="497 U.S. 1", num_results=1, fields=["caseName", "dateFiled", "citation", "opinions", "absolute_url"])`. Returned an irrelevant bankruptcy opinion, Mammola v. Dwyer, 497 B.R. 1 (2013). Disregarded; this showed the citation filter did not isolate the intended authority.
2. `search(type="o", court="scotus", case_name="Milkovich v. Lorain Journal", filed_before="1991-01-01", num_results=2, fields=["caseName", "dateFiled", "citation", "opinions", "absolute_url"])`. Located the June 21, 1990 decision, 497 U.S. 1, including lead opinion 9432089. A separate April 16, 1990 procedural order also appeared and was not used.
3. `search_document(opinion_id=9432089, query="wholesale", snippet_size=1700)`. Read the rejection of a blanket opinion exemption and the explanation that opinion language can imply objective facts.
4. `search_document(opinion_id=9432089, query="rhetorical hyperbole", snippet_size=1100)`. Read the preserved protection for expression not reasonably interpreted as stating actual facts.

No search sought this petition's disposition or subsequent history. No outcome-revealing material about this petition was encountered.
