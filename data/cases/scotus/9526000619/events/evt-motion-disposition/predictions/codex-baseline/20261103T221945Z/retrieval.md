# Retrieval and operational record

## Provisioned inputs

Read the event definition, `record/snapshots/2026-10-28.json`, `record/documents/documents.json`, `record/documents/application.txt`, and `record/context.json`. The application text is whitespace-only and its metadata says `empty_text: true`. No other provisioned filed documents or related-case inputs are present.

## Repository context and commands

- Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, `schemas/agent_tooling.schema.json`, and `schemas/agent_flags.schema.json`. Checked for applicable `AGENTS.md` files; none were found in the checked scope.
- Attempted `uv run fedcourts paths --court scotus --docket 9526000619 --event evt-motion-disposition --role predictor`; failed before retrieval because the default uv cache was read-only. Successfully retried as `uv --no-cache run fedcourts paths --court scotus --docket 9526000619 --event evt-motion-disposition --role predictor`, and later with `UV_NO_CACHE=1 uv run fedcourts paths --court scotus --docket 9526000619 --event evt-motion-disposition --role predictor`. These resolved the case and event paths and withheld the evaluator-only outcome path. No outcome file was read.
- Read `uv --no-cache run fedcourts query --help` and `UV_NO_CACHE=1 uv run fedcourts query --help` before querying. The latter help command was repeated with a narrower displayed excerpt; no corpus transfer occurred for help.
- Read the interim-applications section of `metrics/statpack.md` and queried the interim keys, counts, and Term rows in `metrics/statpack.json` locally with `jq`. The 2016–2025 finer-reading pool totals zero resolved and 1,366 unread; it supplies no eligible baseline. Other-stage rates were not substituted.

## Corpus lookup

Command: `UV_NO_CACHE=1 uv run fedcourts query --court scotus --disposition denied --decided-before 2026 --limit 4`

Transfer: `ranged corpus reads: 13 GET(s), 3407872 byte(s)`

Returned four cert denials, all dated October 19, 2026: *Google LLC v. VirtaMove, Corp., et al.* (25-1230); *Hastings College Conservation Committee, et al. v. California, et al.* (25-1231); *Ryan O'Donnell, et al. v. City of Chicago, Illinois, et al.* (25-1098); and *Utah v. Morris Thomas Mullins* (25-1115). These precede this application's October 27 submission but are not interim comparators. No full opinions were requested and none of these rows calibrated the grant probability. No query was made for the target application's outcome or history.

## Web calls

The following calls returned no usable source content in this execution; none informed the forecast:

1. One search call containing `site.supremecourt.gov Hollingsworth Perry 558 U.S. 183 stay reasonable probability fair prospect irreparable harm` and `site.supremecourt.gov rules Rule 23 stay judgment enforcement application`.
2. Open attempted for `https://www.supremecourt.gov/filingandrules/2023RulesoftheCourt.pdf`.
3. Open attempted for `https://www.supremecourt.gov/opinions/09pdf/09A648.pdf`.

No target-case docket, decision, subsequent history, or news coverage was sought.

## CourtListener MCP

1. `search(type="o", citation="558 U.S. 183", num_results=1, fields=["caseName", "dateFiled", "citation", "absolute_url", "opinions"])`. Returned *Hollingsworth v. Perry*, January 13, 2010, with primary opinion identifiers, including lead opinion 9413203. The search reported four total matches and returned the requested first result; no pagination was requested.
2. `search_document(opinion_id=9413203, query="reasonable probability", snippet_size=850)`. Returned one passage at 558 U.S. 190 identifying the certiorari, reversal, irreparable-harm, and equitable-balancing requirements for a stay. Used only as legal context, not as a fact-matched predictor. Opinion location: `https://www.courtlistener.com/opinion/1747/hollingsworth-v-perry/`.

## Validation

The required cell validator is run with `UV_NO_CACHE=1 uv run fedcourts validate data --cell data/cases/scotus/9526000619/events/evt-motion-disposition/predictions/codex-baseline/20261103T221945Z`. This is a local schema/completeness check, not retrieval of case outcomes.
