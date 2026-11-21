# Evaluator Retrieval Log — `scotus/9526000686` (`evt-motion-disposition`)

## Local CLI & Corpus Queries

- `uv run fedcourts paths --court "scotus" --docket "9526000686" --event "evt-motion-disposition" --role evaluator` — resolved canonical case, corpus, event, and outcome paths (no corpus reads).
- `uv run fedcourts query --court scotus --docket-number 26A623` — stderr: `ranged corpus reads: 21 GET(s), 5505024 byte(s)`. Verified comparator row `scotus/9526000623` (*Jesse Guardado v. Florida*, decided `2026-11-05`, `disposition: "denied"`, `interim_reading: "denied"`, `referred_to_court: true`, `response_requested: false`, `amicus_briefs: 0`).
- `uv run fedcourts query --court scotus --docket-number 26A524` — stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`. Verified comparator row `scotus/9526000524` (*William Reaves v. Florida, et al.*, decided `2026-10-20`, `disposition: "denied"`, `interim_reading: "denied"`, `referred_to_court: true`, `response_requested: false`, `amicus_briefs: 0`).
- `uv run fedcourts query --court scotus --docket-number 26-6154` — stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`. Verified linked certiorari docket `scotus/9026006154` (*Thomas M. Overton v. Florida, et al.*, `originating_docket_number: "SC2026-1724, SC2026-1725"`).
- Read committed `metrics/statpack.md` and `metrics/statpack.json` (`interim` section; verified `statpack_digest` frozen by all three candidates matches the committed build).

## CourtListener MCP Lookups

- `courtlistener.analyze_citations` — checked 9 citations across candidate submissions: verified *Barefoot v. Estelle*, 463 U.S. 880 (1983); *Ohio Adult Parole Authority v. Woodard*, 523 U.S. 272 (1998); *Connecticut Board of Pardons v. Dumschat*, 452 U.S. 458 (1981); *Herrera v. Collins*, 506 U.S. 390 (1993); *Coleman v. Thompson*, 501 U.S. 722 (1991); *Overton v. Jones*, 155 F. Supp. 3d 1253 (S.D. Fla. 2016); and *Overton v. State*, 801 So. 2d 877 (Fla. 2001).
- `courtlistener.search` (`type="o"`, `court="fla"`, `case_name="Sweet v. State"`, `filed_after="2019-01-01"`) — verified *William Earl Sweet v. State of Florida*, No. SC19-195 (filed `2020-02-27`).
- `courtlistener.search` (`type="o"`, `court="fla"`, `case_name="Hunt v. State"`, `filed_after="2024-01-01"`) — verified *Michael H. Hunt v. State of Florida*, No. SC2024-0096 (filed `2025-12-18` / `2026-03-05`).

## Web Searches

- None.
