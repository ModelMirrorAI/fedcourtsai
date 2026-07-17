# Retrieval log — scotus/73281619 evt-petition-disposition (run 20260717T000329Z)

Mode: `forward` (record/context.json).

## Corpus lookups (`fedcourts query`)

1. `uv run fedcourts query --court scotus --citation "42 U.S.C. § 2000cc" --citation "574 U.S. 352" --era 2020s --limit 8`
   → 0 rows. `ranged corpus reads: 419 GET(s), 109707264 byte(s)`
2. `uv run fedcourts query --court scotus --citation "Holt v. Hobbs" --limit 8`
   → 0 rows. `ranged corpus reads: 419 GET(s), 109707264 byte(s)`
3. `uv run fedcourts query --court scotus --topic "religion" --limit 8`
   → 0 rows. `ranged corpus reads: 3 GET(s), 786432 byte(s)`

No matching resolved priors surfaced, so qualitative priors come from the
petition's own documented cert history and general knowledge of the Court's
docket; quantitative anchors come from the committed statpack.

## Base rates

- `metrics/statpack.md` (committed): modern discretionary-cert base rates
  (grant ≈ 2.5–3.3% across Terms 2023–2025), relist and CVSG signal cuts. The
  statpack carries no "Segment base rate by salience band" table in this
  build, and its relist/CVSG cuts do not include a call-for-response cut, so
  the CFR lift is reasoned qualitatively.

## CourtListener MCP

1. `search(type=o, court=scotus, q='RLUIPA "land use"', filed_after=2024-06-01)`
   → 2 results, both *Landor v. Louisiana Dept. of Corrections and Public
   Safety* (decided 2026-06-23) — a RLUIPA damages case, not land-use. Used
   only as context that the Court remains engaged with RLUIPA and has not
   decided the land-use questions. No lookup touched this case's own
   disposition (none exists; the BIO is not due until 2026-08-14).

## Web searches

None.
