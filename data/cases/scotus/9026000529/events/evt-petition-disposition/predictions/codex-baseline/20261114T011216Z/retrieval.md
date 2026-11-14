# Retrieval record

## Provisioned record and local context

Read the event definition, November 14, 2026 snapshot, context.json, documents.json, questions-presented.txt, petition.txt, relevant appendix excerpts, and same-question.json. Read the prediction contract, output schemas, and metrics/statpack.md; inspected metrics/statpack.json's Term/band aggregates and pooled the strictly prior baseline risk sets with jq. No outcome file, other prediction/evaluation, or data/qp-topics content was read. An initial overbroad local file-name listing was truncated; it exposed path names, including outcome.json paths, but no file contents and no information used as outcome evidence.

## CLI attempts

1. `uv run fedcourts paths --court scotus --docket 9026000529 --event evt-petition-disposition --role predictor` failed because the default uv cache under the home directory was unwritable. No retrieval occurred.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000529 --event evt-petition-disposition --role predictor` succeeded and confirmed the case/event paths; the outcome path was expressly withheld as evaluator-only. No transfer line.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` returned the structured-filter CLI help. No transfer line.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition denied --era 2020s --decided-before 2026 --limit 3` succeeded. Stderr: `ranged corpus reads: 8 GET(s), 2031616 byte(s)`. Returned Jesenik (25-7515), MacRitchie (25-7522), and Waidla (25-7555), all denied November 9, 2026, before this forward cell's November 14 vantage. The clock option is year-derived, not a strict January 1 date boundary. None concerns this cell's case; no opinion bodies were requested. These issue-unmatched denial-filtered rows were not used as a statistical estimate.

## Web attempts

5. A web.run batch searched `site.supremecourt.gov opinions Holmes South Carolina 547 319 2006 evidence` and `site.uscode.house.gov 28 USC 1259 refused to grant petition review`. The tool returned no visible results or source text. Nothing was relied on.
6. A second web.run batch searched `Holmes South Carolina 547 319 arbitrary disproportionate evidence 2006` and `28 USC 1259 refused to grant`. Again no visible results or source text. Nothing was relied on. Neither batch sought Becker's outcome or a forecast.

## CourtListener MCP

7. `search(type="o", citation="547 U.S. 319", num_results=1)` succeeded, returning Holmes v. South Carolina, May 1, 2006, opinion/cluster 145659, docket 04-1327. The result reported six matches; only the first was requested/read.
8. `search_document(opinion_id=145659, query="arbitrary", snippet_size=1300)` succeeded. Read excerpts explaining the arbitrary/disproportionate exclusion standard, the legitimacy of ordinary evidentiary balancing, and the defect in South Carolina's strength-of-prosecution-evidence rule. Used as general precedent, not as a factual analogue or evidence about Becker's eventual disposition.

The final cell-validation command is a local output/schema check, not substantive retrieval.
