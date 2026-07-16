# Retrieval

## Corpus and base rates

- Consulted `metrics/statpack.md` and the 2025 paid-fee detail in `metrics/statpack.json`.
- Attempted: `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation 'CIGNA Corp. v. Amara' --citation 'Mertens v. Hewitt Associates' --limit 10 --corpus-backend ranged`.
  - Result: failed because the runner could not resolve the corpus remote's host. No `ranged corpus reads: …` line was emitted.

## CourtListener MCP

- Opinion search for `"equitable surcharge" AND "1132(a)(3)"`, limited to decisions filed after January 1, 2023; returned *Stark*, the Sixth Circuit decision below, and *Aramark*.
- Opinion searches for *Aramark Services v. Aetna Life Insurance* (one name-filter search returned no results; a keyword search returned the Fifth Circuit decision).
- Retrieved metadata for *Aramark*, cluster 10761003, and its combined opinion, opinion 11227588.
- Retrieved metadata for the related *Aramark* appellate docket, docket 69183199.
- Retrieved the docket-entry endpoint schema and the ten latest *Aramark* docket entries. The returned entries showed a rehearing-en-banc petition and response through February 12, 2026.
- Opinion search for *Stark v. Reliance Standard Life Insurance Company*.
- Retrieved metadata for *Stark*, cluster 10624483, and its opinion, opinion 11091071.

No web searches were used. I did not search for this Supreme Court petition's disposition or post-snapshot docket history.
