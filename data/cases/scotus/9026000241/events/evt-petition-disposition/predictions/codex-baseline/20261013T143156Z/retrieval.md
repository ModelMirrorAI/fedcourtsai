# Retrieval record

## Local inputs and aggregate context

- Read AGENTS.md, .github/prompts/predict.md, prediction/flags/tooling schemas, the specified event, record/context.json, record/snapshots/2026-10-13.json, and provisioned questions-presented, petition, appendix, and document manifest. The appendix review concentrated on the appellate opinion and the district court's retaliation analysis, not every reproduced filing.
- Read metrics/statpack.md: modern-cert disposition, originating-circuit, paid-segment relist/CVSG and salience cuts, and the sal-v4 per-Term reached table. Read aggregate fields in metrics/statpack.json and pooled baseline reached estimates only over Terms 2017-2025: 642 / 12,871 = 0.0498795742. Did not use the 2026 row as an anchor.
- Ran git log -1 --format='%h %cI' -- metrics/statpack.json: ea0a1e70a, 2026-10-12T21:45:55Z. This dates the committed artifact, not its underlying corpus pulls.
- Ran uv run fedcourts paths --court scotus --docket 9026000241 --event evt-petition-disposition --role predictor. The default cache location was read-only; reran successfully with a writable temporary cache. No outcome file was read.
- Ran uv run fedcourts corpus-info with the temporary cache. It failed because the service backend has no client-side connection. No vintage or corpus rows were returned, and no ranged corpus reads line was printed. No fedcourts query or open-events call was made.
- Read the package path and serialization helpers to resolve and write this cell, and used the schemas/validator for output checks. These are tooling reads, not case evidence.

## External legal context

1. Web search: site.supremecourt.gov opinions 2024 Gonzalez Trevino Nieves objective evidence 23-334. No usable result was returned; no evidentiary weight assigned.
2. Attempted web open of a Supreme Court PDF path ending 23pdf/23-334_d1o2.pdf. No content returned. This unverified path was not used as a citation or source.
3. CourtListener MCP search: type=o, citation=602 U.S. 653, num_results=2. Located Gonzalez v. Trevino, June 20, 2024, including opinion 11066659.
4. CourtListener MCP search_document: opinion_id=11066659, query=overly cramped, snippet_size=1800. Read the objective-evidence rule and rejection of a rigid identical-comparator requirement.
5. CourtListener MCP search: type=o, citation=143 F.4th 914, num_results=1. Returned no matches; not treated as proof the authority is absent.
6. CourtListener MCP search: type=o, case_name=Murphy v. Schmitt, filed_before=2026-10-13, num_results=2. Located Mason Murphy v. Michael Schmitt, Eighth Circuit, July 9, 2025, docket 22-1726, opinion 11092467. Disregarded the unrelated Massachusetts result.
7. CourtListener MCP read_document: opinion_id=11092467. Retrieved the appellate opinion; displayed output was partially truncated.
8. CourtListener MCP search_document: opinion_id=11092467, query=bolster, snippet_size=1400. Read the majority's pleading-stage explanation and footnote 3, as well as the dissent's objection.

No search sought Rahdar's Supreme Court outcome or subsequent history. No outcome-revealing material about this petition surfaced. No corpus transfer statistics are claimed beyond the absence of a transfer line on the unsuccessful corpus-info command.
