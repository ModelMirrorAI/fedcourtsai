# Retrieval log

## Local context beyond provisioned case inputs

- Read `metrics/statpack.md`: modern discretionary-cert disposition and circuit context, paid-segment relist/CVSG cuts, per-Term table, and sal-v4 reached-band table.
- Read selected metadata and Term/segment fields in `metrics/statpack.json`. Used `jq` to pool elevated reached rates over displayed Terms 2017–2024: numerator 484, weighted denominator 2,810, rate 0.17224199288256228. The initial inspection of the first Term object displayed the 2026 row; no 2025 or 2026 rate was used in the anchor.
- Ran `git log -1 --format='%h %cI' -- metrics/statpack.json` to identify the committed artifact vintage: September 14, 2026 at 11:02 UTC. No live corpus freshness claim is made.
- Read task/schema contracts and used `fedcourts paths` for the supplied identifiers. The first CLI invocation failed because its default cache directory was read-only; retrying with a temporary writable cache and `--no-sync` succeeded.
- No `fedcourts query` or `open-events` calls; no ranged corpus reads stderr lines. No CourtListener MCP lookups.

## Web retrieval: general precedent only

- Submitted searches: `site.supremecourt.gov opinions 2020 19-251 Americans for Prosperity Bonta exacting scrutiny narrow tailoring` and `site.supremecourt.gov Rule 10 certiorari compelling reasons conflict`. These initial calls returned no usable displayed result; no Rule 10 source was relied on.
- Attempted to open the official Bonta opinion at `https://www.supremecourt.gov/opinions/20pdf/19-251_p86b.pdf`; no usable displayed result was returned.
- Searched `site.supremecourt.gov/opinions/20pdf/19-251_p86b.pdf`; no usable displayed result was returned.
- Retried opening the same official PDF; no usable displayed result was returned. No external opinion text or search-result facts entered the forecast. The Bonta discussion rests on the provisioned petition and opposition instead.

No search used this petition's caption, docket number, outcome, or subsequent history. No outcome of this petition surfaced. The NRSC reference came only from the provisioned opposition, not external retrieval.
