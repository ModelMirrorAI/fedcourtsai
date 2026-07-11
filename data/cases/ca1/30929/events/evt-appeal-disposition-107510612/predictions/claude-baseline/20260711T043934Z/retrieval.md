# Retrieval log — claude-baseline / 20260711T043934Z

## Corpus lookups (`fedcourts` CLI, ranged reads against the remote)

- `uv run fedcourts query --court ca1 --limit 20`
  — `ranged corpus reads: 27 GET(s), 7077888 byte(s)`
  — 20 priors; dispositions {other: 15, denied: 3, dismissed: 2}.
- `uv run fedcourts query --court ca1 --topic "3440 Other Civil Rights" --limit 10`
  — `ranged corpus reads: 258 GET(s), 67633152 byte(s)`
  — 1 prior (ca1/4680, 18-1898, decided 2019-06-27, disposition `other`).

## Base rates

- Read `metrics/statpack.md` (committed roll-up): its sections are SCOTUS-cert
  cuts only; no circuit-appeal disposition base rates were available to use.

## CourtListener MCP

- Attempted 2 `search` calls (RECAP docket lookup for the originating district
  case, D.P.R. 3:18-cv-01993, restricted to pre-appeal fields/dates). **Both
  failed server-side** with `REDIS_URL is not set; cannot access session store`.
  No CourtListener data informed this prediction.
- Deliberately did **not** query this case's own appellate docket or any
  post-appeal history, to avoid retrieving the outcome (see `reasoning.md`).

## Web searches

- None.
