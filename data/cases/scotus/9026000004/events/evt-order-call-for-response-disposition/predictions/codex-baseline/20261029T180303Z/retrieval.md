# Retrieval record

No lookup sought this case's disposition or subsequent history. Case facts came only from the provisioned August 14 snapshot and pre-boundary petition, including its appellate appendix. No CourtListener MCP lookup was attempted. No other cell's output or labeling artifact was read.

## Corpus and committed statistical context

- Read `metrics/statpack.md`: modern discretionary-cert anchor; paid-segment relist, CVSG, and amicus cuts; matching `sal-v4` per-Term reached-band table. Read `metrics/statpack.json` to inspect the structure and calculate the strictly-prior baseline pool: 660 / 12,913 = 0.0511112832 over 2017–2025. The current Term is excluded. No fresh corpus aggregate was obtained.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` was consulted before querying; two later invocations printed portions of the same help to recover the flags from truncated terminal output. Help only; no case rows were returned by these commands.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --citation '600 U.S. 122' --limit 3`
  - Returned no rows. The notice said only 200 SCOTUS rows in scope carry reporter citations and warned that an empty result likely reflects sparse coverage. I did not retry the sparse citation filter.
  - Transfer stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts corpus-info --help`: inspected vintage-report options.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts corpus-info`: failed with `ValueError: the service backend has no client-side connection`; no blob vintage or newest-pull/newest-snapshot figure was obtained. No fallback credentials or direct remote requests were attempted.

## General precedent, official Court source

All web calls concerned **Mallory**, not Samsung or Brewer. They were:

1. Search query `site.supremecourt.gov opinions 2022 Mallory Norfolk Southern 21-1168 pdf`: returned the Court's June 27, 2023 slip opinion.
2. Opened `https://www.supremecourt.gov/opinions/22pdf/21-1168_f2ah.pdf`: received the official opinion, syllabus, and its notice/consent discussion.
3. Searched within that PDF for `judicial precedent`: returned the precedent's discussion of consent, notice, and state-law interpretation.
4. Searched within the same PDF for `authoritative`: returned the discussion of Pennsylvania Fire's state-supreme-court construction of a registration law.
5. Opened that same PDF again: the returned extract included footnote 5, rejecting a magic-words requirement, referencing Georgia, and reserving other schemes and facts. This qualified the petition's express-statutory-notice characterization. I did not retrieve any later Mallory proceedings.

## Local contract and validation helpers

- Read `AGENTS.md`, the prediction prompt, prediction/tooling/flags schemas, and searched for scoped `AGENTS.md` files. No additional scoped instructions were found under data.
- `uv run fedcourts paths --court scotus --docket 9026000004 --event evt-order-call-for-response-disposition --role predictor`: first attempt failed before execution because uv's default cache was read-only. Reissued successfully with `UV_CACHE_DIR=/tmp/uv-cache`; it reported only the case/corpus/event paths, not an outcome.
- Inspected `fedcourtsai.paths` and `fedcourtsai.serialize` to use repository path and serialization helpers; read `fedcourts validate --help`. These are implementation/contract checks, not case retrieval.
- All substantive case inputs, statistical files, and retrievals used in the forecast are enumerated here. Validation and JSON normalization are local checks, not additional evidence.
