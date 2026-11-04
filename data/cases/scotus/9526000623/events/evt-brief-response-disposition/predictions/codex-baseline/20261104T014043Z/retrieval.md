# Retrieval beyond the provisioned record

No search sought this application's disposition, subsequent history, or coverage of its decision. The linked petition's outcome was not retrieved. Local schema and prompt reads are contract inspection, not outcome retrieval.

## Local tooling and base rates

- `uv run fedcourts paths --court scotus --docket 9526000623 --event evt-brief-response-disposition --role predictor` initially failed because uv's default cache directory was read-only. It performed no case retrieval. Repeated successfully with `UV_CACHE_DIR=/tmp/uv-cache`; it resolved the case and event paths and withheld the evaluator-only outcome path.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` inspected the structured query options. A second help invocation with `COLUMNS=160` made the clock and filter descriptions readable. Neither was a corpus lookup.
- Read the interim section of `metrics/statpack.md`, and inspected `metrics/statpack.json` with jq. Computed the 2016–2025 finer-reading pool: 0 resolved, 0 granted, 1,366 unread; the required baseline is unavailable. No older substantive rate was substituted.

## Corpus lookup

Command: `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition denied --era 2020s --decided-before 2026 --limit 4`

Transfer report: `ranged corpus reads: 13 GET(s), 3407872 byte(s)`

Returned Google LLC v. VirtaMove, Corp., et al. (25-1230); Hastings College Conservation Committee, et al. v. California, et al. (25-1231); Ryan O'Donnell, et al. v. City of Chicago, Illinois, et al. (25-1098); and Utah v. Morris Thomas Mullins (25-1115). These were cert denials dated October 19, 2026, on earlier-Term petitions. They were not comparable clemency stay applications and were not used as a grant-rate estimate. No opinion bodies were requested.

## Web attempts

1. `web.run` search: `site.supremecourt.gov opinions boundvolumes 523bv Woodard 272`. The tool returned no visible results or source text; no evidence was obtained.
2. `web.run` search: `Ohio Adult Parole Authority v Woodard 523 U.S. 272 O'Connor 289 clemency`. The tool again returned no visible results or source text. Neither search included this applicant or application.

## CourtListener MCP

1. `search(type="o", citation="523 U.S. 272", num_results=1)`: returned an inapposite first hit, Pegram v. Honeywell, Inc., 361 F.3d 272 (5th Cir. 2004). Its opinion was not opened and it was not relied on. The citation filter did not isolate the intended authority.
2. `search(type="o", court="scotus", case_name="Ohio Adult Parole Authority v. Woodard", num_results=1)`: returned the intended Supreme Court decision, March 25, 1998, 523 U.S. 272, cluster 118189, with constituent opinion identifiers.
3. `read_document(opinion_id=9433600)`: read Justice O'Connor's concurrence, 5,098 characters, addressing minimal procedural safeguards in clemency. Used its narrow access/arbitrariness framework and its rejection of the particular alleged procedural defects. Citation: Ohio Adult Parole Authority v. Woodard, 523 U.S. 272, 288–90 (1998).

No CourtListener REST fallback, package installation, or other live-case lookup was attempted. Validation is a local output-contract check, not additional factual retrieval.
