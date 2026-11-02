# Retrieval record

## Local inputs and tooling

- Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, and the tooling/flags schemas; inspected the event definition, the case-level October 17 snapshot, and context. The record file listing contained no provisioned filed documents or related dockets. No other predictor or evaluator output was read.
- Read only the interim-applications section of `metrics/statpack.md` substantively; a heading search located it. Pooled the 2016–2025 rows: 160 grants / 1,366 resolved substantive applications. An initial whole-file awk calculation also matched unrelated table rows and was discarded; the section-restricted calculation produced the figures used in this forecast.
- Attempted `uv run fedcourts paths --court scotus --docket 9526000606 --event evt-motion-disposition --role predictor`; uv could not initialize its read-only default cache. Reissued successfully with `UV_CACHE_DIR=/tmp/uv-cache`. It resolved the event path and identified the outcome as evaluator-only; no outcome file was opened. The temporary cache setting was used on subsequent uv commands, with no package installation.
- Ran `uv run fedcourts query --help` twice, with that cache override. The output described the structured filters and application scope; a later usage error provided the complete era vocabulary.

## Corpus queries

1. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition denied --era roberts --decided-before 2026 --limit 4`
   - Rejected: `roberts` is not an era token; the interface requires decade tokens. No corpus transfer line was printed.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition denied --era 2020s --decided-before 2026 --limit 4`
   - `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
   - Returned Google LLC v. VirtaMove, Corp., et al. (25-1230); Hastings College Conservation Committee, et al. v. California, et al. (25-1231); Ryan O'Donnell, et al. v. City of Chicago, Illinois, et al. (25-1098); and Utah v. Morris Thomas Mullins (25-1115). All were denied cert petitions with no opinion body. They are not matched interim/removal comparators and do not determine the probability. The Term-year filter can admit prior-Term petitions resolved in the current calendar year; this is a forward cell, and none is the target application.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '556 U.S. 418' --decided-before 2026 --limit 1`
   - `ranged corpus reads: 8 GET(s), 2097152 byte(s)`
   - No rows; explicit warning that only 200 scoped rows carried reporter citations, making an empty result a coverage limitation rather than absence of the precedent.

## Web attempts

The following `web.run` calls returned no usable result content to this session; no case facts or legal propositions were inferred from them:

1. Search: `site.supremecourt.gov Nken Holder 556 U.S. 418 stay removal four factors 2009`.
2. Search: `Nken v Holder 556 U.S. 418 2009 Supreme Court opinion`.
3. Open: the govinfo U.S. Reports PDF for volume 556, page 418 (`USREPORTS-556-418.pdf`).

## CourtListener MCP

1. `search(type="o", citation="556 U.S. 418", num_results=1)` returned Nken v. Holder, decided April 22, 2009, opinion/cluster 145884, docket 08-681. The returned metadata linked the official Supreme Court opinion. This is general legal context, not the target case.
2. `search_document(opinion_id=145884, query="four factors", snippet_size=1000)` returned two excerpts, including the traditional stay factors at U.S. Reports pages 426 and 434. Those excerpts support the legal-context discussion in `reasoning.md`; they contain no target-case material.

No target-case web search, live docket retrieval, subsequent-history lookup, or outcome retrieval was attempted. No `--full` corpus bodies were requested. Validation is a local output-contract check, not additional case retrieval.
