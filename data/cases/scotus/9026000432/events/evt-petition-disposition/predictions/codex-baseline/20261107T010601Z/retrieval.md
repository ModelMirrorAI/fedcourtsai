# Retrieval and tooling log

## Local contract and context

Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, `schemas/agent_flags.schema.json`, and `schemas/agent_tooling.schema.json`; inspected the event and case-level provisioned inputs. Read the committed `metrics/statpack.md`, particularly modern cert dispositions, originating-circuit context, paid-segment relist/CVSG/amicus cuts, and prior-Term reached-band rates. No other prediction, evaluation, outcome file, or topic-label artifact was read.

## Corpus CLI calls

1. `uv run fedcourts paths --court scotus --docket 9026000432 --event evt-petition-disposition --role predictor` failed before execution because uv's default cache was on a read-only filesystem. No transfer line.
2. `uv run fedcourts query --help` failed for the same cache reason. No transfer line.
3. `UV_CACHE_DIR=/tmp/fedcourts-uv-cache UV_NO_SYNC=1 uv run fedcourts paths --court scotus --docket 9026000432 --event evt-petition-disposition --role predictor` succeeded and confirmed the event path; no outcome was opened. No transfer line.
4. `UV_CACHE_DIR=/tmp/fedcourts-uv-cache UV_NO_SYNC=1 uv run fedcourts query --help` succeeded and described structured filters. No transfer line.
5. `UV_CACHE_DIR=/tmp/fedcourts-uv-cache UV_NO_SYNC=1 uv run fedcourts query --court scotus --disposition denied --era modern --decided-before 2026 --limit 3` was rejected because `modern` is not a valid era; the CLI supplied the decade vocabulary. No transfer line.
6. `UV_CACHE_DIR=/tmp/fedcourts-uv-cache UV_NO_SYNC=1 uv run fedcourts query --court scotus --disposition denied --era 2020s --decided-before 2026 --limit 3` succeeded. It returned Google LLC v. VirtaMove (25-1230), Hastings College Conservation Committee v. California (25-1231), and Ryan O'Donnell v. Chicago (25-1098), all recorded denied October 19, 2026. The optional Term filter selects their prior docket-number Term; these dates also precede this forward forecast. None is the target petition. No opinion text requested. These are generic procedural context, not issue-matched comparisons.

   `ranged corpus reads: 14 GET(s), 3670016 byte(s)`

## Web attempts

The following `web.run` attempts returned no visible content or usable sources. No web result was used as evidence:

1. Search batch: `site.supremecourt.gov rules Rule 10 petition writ certiorari judicial proceedings`; `site.ca2.uscourts.gov Pillay INS 45 F.3d 14 frivolous`.
2. Search batch: `Supreme Court Rule 10 error correction judicial proceedings`; `"Clark v. Sweeney" "2025"`; `"Margolin" "National Association of Immigration Judges" "2026"`.
3. Open attempt: `https://www.supremecourt.gov/filingandrules/2023RulesoftheCourt.pdf`.

These were general authority lookups, not a search for this petition's outcome. The petition's recent-authority characterizations remain unverified.

## CourtListener MCP

1. `search(type="o", citation="45 F.3d 14", num_results=2)` returned 19 broad citation matches; the displayed results were unrelated district-court cases. They were not used substantively.
2. `search(type="o", court="ca2", case_name="Pillay", num_results=3, fields=["caseName","citation","dateFiled","opinions","absolute_url"])` returned the matching *Joshua Pillay v. Immigration and Naturalization Service*, 45 F.3d 14, January 3, 1995, opinion 686765.
3. `read_document(opinion_id=686765)` returned the opinion text. Used its recognition of inherent authority to dismiss frivolous paid appeals and its caution to protect nonfrivolous claims, pages 16–17. No quotation reproduced.

## Validation

Use `UV_CACHE_DIR=/tmp/fedcourts-uv-cache UV_NO_SYNC=1 uv run fedcourts validate data --cell data/cases/scotus/9026000432/events/evt-petition-disposition/predictions/codex-baseline/20261107T010601Z` to check the completed cell. Validation is local, not substantive retrieval.
