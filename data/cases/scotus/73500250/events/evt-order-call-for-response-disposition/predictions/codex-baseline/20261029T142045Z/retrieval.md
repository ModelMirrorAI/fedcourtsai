# Retrieval record

## Provisioned inputs

Read the event definition, July 27, 2026 snapshot, context, document manifest, questions-presented extract, and selected substantive portions of the petition including the appended lower-court opinion. No later docket, realized Supreme Court outcome, other cell's output, or labeling artifact was read.

## Corpus commands and aggregate context

- `uv run fedcourts paths --court scotus --docket 73500250 --event evt-order-call-for-response-disposition --role predictor` initially failed because uv's default cache was on a read-only filesystem. Repeated with `UV_CACHE_DIR=/tmp/uv-cache`; returned the case, corpus, and event paths, with the outcome withheld as evaluator-only. This was path discovery, not a corpus-prior retrieval.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` succeeded. Repeated as `COLUMNS=130 UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help | sed -n '36,105p'` to read options obscured by terminal wrapping/truncation.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition denied --decided-before 2025 --limit 3` succeeded. Its exact transfer line was:

  `ranged corpus reads: 43 GET(s), 11272192 byte(s)`

  It returned National Rifle Association v. Glass (24-1185), Bivens v. Second Amendment Foundation (24-1329), and Tripathy v. McKoy (24-229), all marked denied, all with distribution count four and no hydrated opinion. They are unrelated, selected denials rather than a representative sample, and provide no topical or response-request-specific rate. Although the filter is a prior-Term mask, returned resolution dates are in June 2026; this is a forward cell and those dates precede its staged July moment. None is this case or an identified companion. No further corpus lookup was made.
- Read the committed `metrics/statpack.md` modern-cert and paid-segment cuts and sal-v4 reached-band table. A read-only statistical subagent consulted only this pack and `metrics/statpack.json` to pool all displayed prior-Term baseline risk sets; I checked the table and aggregate field definitions. The resulting committed-pack anchor is 607/11,599, or 5.2332%. No live aggregate refresh or corpus freshness figure was obtained. The subagent did not read case files or conduct external retrieval.

## External calls, including failures

1. Web search with queries `site.supremecourt.gov opinions 2024 Barnes Felix 23-1239 totality circumstances` and `site.ca5.uscourts.gov 242 bodily injury Brugier`. The latter spelling was a search-term error. The tool returned no visible result or usable source; neither query provided evidence.
2. Web search with query `site.supremecourt.gov/opinions "Barnes" "Felix" "2025"`. Again no visible result or usable source. No page was opened.
3. CourtListener MCP `search(type="o", citation="544 F.3d 88", num_results=1)` to check United States v. Cote, a precedent cited in the staged petition. Returned HTTP 429, daily rate limit exceeded, estimated retry availability 1,340 seconds. No opinion or substantive search result was returned. I did not wait, extract credentials, or use direct REST.

No external source informed a factual conclusion about this case. General procedural judgments and the distinctions between the petition's arguments and the attached opinion rest on the staged record, with unverified split assertions identified as such.

## Output checks

Local model/schema checks and `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts validate data` are artifact validation, not case-outcome retrieval. These checks do not authorize consulting evaluator-only material.

Prediction, flags, and tooling each passed their Pydantic model validation. The exact prior-Term anchor was independently recomputed locally. Full validation completed successfully: `OK: 29701 artifact(s) valid, 71057 reference(s) consistent`. A read-only statistical review of this cell's numerical claims reported no blockers. Working-tree status showed only the new prediction-output tree; no commit, push, or PR operation was performed.
