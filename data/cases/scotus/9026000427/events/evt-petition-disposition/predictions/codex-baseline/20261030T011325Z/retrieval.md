# Retrieval beyond the provisioned record

## Local context and corpus commands

- Read the committed `metrics/statpack.md`, especially the modern discretionary-cert, paid-segment relist/CVSG/amicus cuts, and sal-v4 per-Term band table. Computed a denominator-weighted pool of the published baseline reached rates for Terms 2017–2025: n=12,913, approximately 5.106823%. No 2026 row entered the anchor. These are committed-pack figures; corpus-wide newest pull and snapshot vintage could not be established in this service-only cell.
- `uv run fedcourts paths --court scotus --docket 9026000427 --event evt-petition-disposition --role predictor`: first attempt failed because the default uv cache was read-only. Repeated with `UV_CACHE_DIR=/tmp/uv-cache` twice successfully; obtained case and event paths. Did not open the evaluator-only outcome.
- `uv run fedcourts query --help`: first attempt failed on the same uv cache permission error. Repeated with `UV_CACHE_DIR=/tmp/uv-cache` successfully twice, the second time displaying the leading help section. No corpus rows were requested by help.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition denied --era modern --decided-before 2026 --limit 3`: rejected locally because `modern` is not a supported decade token. No corpus-read transfer line was returned.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition denied --era 2020s --decided-before 2026 --limit 3`: executed successfully **twice**. Each returned Google LLC v. VirtaMove (scotus/73265705), Hastings College Conservation Committee v. California (scotus/73266074), and Ryan O'Donnell v. City of Chicago (scotus/73281381), all unrelated Term-2025 denied petitions. These filtered rows were not used to estimate grant frequency or establish a whistleblower precedent. Each execution reported:

  `ranged corpus reads: 0 GET(s), 0 byte(s)`

- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts corpus-info`: failed with `ValueError: the service backend has no client-side connection`; no vintage stamps or transfer line were returned. No corpus pull or alternative credential path was attempted.

## CourtListener MCP

1. `search(type="o", citation="162 F.3d 665", num_results=1)`: one result, John P. Bosley v. Merit Systems Protection Board, Federal Circuit, December 14, 1998, opinion 759750.
2. `read_document(opinion_id=759750)`: returned the 23,345-character opinion, with the tool display truncating part of its middle. Read the returned opening, continuing-pay discussion, and conclusion. It distinguishes the old pay decision from separate alleged later reprisals and affirms in part, vacates in part, and remands. No lookup of Coleman's Supreme Court outcome or subsequent history was made.

## Web attempts

1. Search: `site.supremecourt.gov Rule 10 rarely granted erroneous factual findings misapplication properly stated rule law`. The tool returned no usable displayed result.
2. Open: the Supreme Court's official `filingandrules/2023RulesoftheCourt.pdf` resource. The tool returned no usable displayed content.
3. Find within that resource for `erroneous factual`. The tool returned no usable displayed content.

No legal proposition was treated as verified from those empty web responses. No case-specific outcome search was attempted. The prediction relies on the provisioned petition and appendix, committed base rates, and the independently retrieved Bosley precedent.
