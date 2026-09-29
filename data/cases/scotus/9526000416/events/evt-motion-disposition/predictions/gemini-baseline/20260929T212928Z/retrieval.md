- Read `metrics/statpack.md` for interim application base rates.
- `uv run fedcourts query --court scotus --decided-before 2026-09-29 --include-applications`
  `note: replay cutoff 2026-09-29 (from --decided-before) — priors that had not resolved by then are excluded, on top of any --decided-before Term`
  `ranged corpus reads: 7 GET(s), 1703936 byte(s)`
