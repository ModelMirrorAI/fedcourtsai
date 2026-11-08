# Retrieval record

## Provisioned inputs and local reference material

Read the prediction contract and prediction/tooling schemas; the event definition; `record/snapshots/2026-11-08.json`; `record/context.json`; and `record/documents/documents.json`, `questions-presented.txt`, `petition.txt`, and relevant appendix opinions and orders. Read the committed `metrics/statpack.md` cert disposition, circuit, relist, CVSG, amicus, and sal-v8 reached-band tables; inspected top-level keys of `metrics/statpack.json`. No other cell's output, evaluator-only outcome, or topic-labeling artifact was read.

`uv run fedcourts paths --court scotus --docket 9026000367 --event evt-petition-disposition --role predictor` initially failed because the default uv cache was read-only. Repeating it with `UV_CACHE_DIR=/tmp/uv-cache` succeeded and resolved the case/event paths. No package was installed. `uv run fedcourts query --help` was consulted twice, the second time with `COLUMNS=120` and a shortened display; these were interface checks, not corpus reads. Subsequent uv commands used the same temporary cache override.

## Corpus lookups

1. Attempted `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition denied --era roberts --decided-before 2026 --limit 4`. Rejected locally because era must be a decade token. Returned the valid flag vocabulary; no transfer line was emitted. Corrected the era rather than abandoning retrieval.
2. Ran `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition denied --era 2020s --decided-before 2026 --limit 4`. Returned four denied petitions: Google LLC v. VirtaMove, Corp., et al. (25-1230), Hastings College Conservation Committee, et al. v. California, et al. (25-1231), Ryan O'Donnell, et al. v. City of Chicago, Illinois, et al. (25-1098), and Utah v. Morris Thomas Mullins (25-1115). These are prior-docket examples, not verified subject-matter matches or an unbiased rate sample. No opinion bodies were requested. The Term mask is conservative for this forward cell; the returned prior-Term docket records carried October 19, 2026 denial dates, still before this prediction.

   Exact stderr transfer line: `ranged corpus reads: 14 GET(s), 3670016 byte(s)`.

## General web attempts

All seven web-tool calls below returned no readable content or source citation identifiers. They sought general Court rules, never this case or its disposition. None supplied facts used in the forecast.

1. Search: `site.supremecourt.gov Rules Rule 10 writ certiorari state law misapplication`.
2. Open: `https://www.supremecourt.gov/filingandrules/rules_guidance.aspx`.
3. Open: `https://www.supremecourt.gov/filingandrules/2023RulesoftheCourt.pdf`.
4. Repeat open: `https://www.supremecourt.gov/filingandrules/rules_guidance.aspx`.
5. Repeat open: `https://www.supremecourt.gov/filingandrules/rules_guidance.aspx`.
6. Repeat open: `https://www.supremecourt.gov/filingandrules/rules_guidance.aspx`.
7. Open: `https://www.supremecourt.gov/filingandrules/2026RulesoftheCourt_WEB.pdf`.

No CourtListener MCP lookup was made. No live docket or subsequent-history search was attempted. The lower-court decision was read from the provisioned appendix instead.

## Validation

Ran the contract's cell-scoped `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts validate data --cell data/cases/scotus/9026000367/events/evt-petition-disposition/predictions/codex-baseline/20261108T010928Z`. It returned `OK: 29934 artifact(s) valid, 71209 reference(s) consistent; cell complete`. Repeated validation after recording this result. This checks output integrity, not additional case evidence.
