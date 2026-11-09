# Retrieval record

## Provisioned and local reference material

Read the prediction contract, prediction/tooling/flags schemas, event definition, case-level context, November 3 snapshot, and application text/metadata. Consulted the committed interim section of `metrics/statpack.md` and the corresponding `metrics/statpack.json` counts. Pooled only application-Terms 2016–2025, including the private/unmarked applicant cut. No other prediction, evaluation, realized-outcome file, or QP-topic artifact was read.

## Corpus and CLI calls

1. `uv run fedcourts paths --court scotus --docket 9526000657 --event evt-motion-disposition --role predictor` failed before execution because the default uv cache directory was read-only. Repeated with `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts paths --court scotus --docket 9526000657 --event evt-motion-disposition --role predictor`; it resolved the case and event paths and did not provide an outcome path.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --help` returned the supported structured filters. Repeated help with `COLUMNS=140`, displaying a narrower portion, to inspect the options. Neither is a corpus-result lookup.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --disposition denied --era 2020s --decided-before 2026 --limit 5` returned five denied cert petitions: Google LLC v. VirtaMove (25-1230), Hastings College Conservation Committee v. California (25-1231), Ryan O'Donnell v. City of Chicago (25-1098), Utah v. Mullins (25-1115), and Amy Hadley v. City of South Bend (25-1158). They are not application comparators and received no numerical weight. The first command's transfer line was not visible in the truncated output. Repeated the identical query with output reduced through `jq`; its transfer line was `ranged corpus reads: 0 GET(s), 0 byte(s)`. The repeat returned the same five cases. No bodies were requested. The Term filter concerns the docket Term, not necessarily its resolution date; the visible dispositions were October 19, 2026, before this application's submission.

## CourtListener MCP

1. `search(type="r", court="ca4", docket_number="26-2406", filed_before="2026-11-03", num_results=5, fields=["docket_id", "caseName", "docketNumber", "dateFiled", "court", "absolute_url"])`: query ID `215ba829`, zero results. This was an attempt to identify the lower-court record, not the Supreme Court application's outcome. No further endpoint or document requests were made.

## Web attempts

All three calls returned no usable result or document content. No legal proposition or case outcome was learned from them.

1. Opened the general official rules PDF address `https://www.supremecourt.gov/filingandrules/2023RulesoftheCourt.pdf`.
2. Searched `site.supremecourt.gov Rule 23 stay application relief lower court`.
3. Attempted to open `https://www.supremecourt.gov/filingandrules/2026rulesofthecourt_web.pdf`; its existence was not verified.

No search for this Supreme Court application's disposition or subsequent history was attempted. No live Supreme Court docket was opened.
