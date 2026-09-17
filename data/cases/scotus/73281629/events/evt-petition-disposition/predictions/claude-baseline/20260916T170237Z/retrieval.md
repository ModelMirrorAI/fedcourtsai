# Retrieval log

## Corpus (`fedcourts query`)

1. `uv run fedcourts query --court scotus --text "ERISA 1024(b)(4) disclosure plan documents" --limit 8` — rejected: `query` takes no free-text argument. No corpus read.
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 6` — `ranged corpus reads: 23 GET(s), 6029312 byte(s)`. Returned recent granted SCOTUS rows (mostly OT2025 substantive applications); nothing ERISA-specific, not used in the forecast beyond confirming the corpus carries no subject filter for SCOTUS rows.
3. `uv run fedcourts query --court scotus --era 2020s --limit 6` — `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm cache). Same character; not used.

## Base rates

- `metrics/statpack.md`: "Modern discretionary-cert petitions by disposition", "by originating circuit" (ca9 row), "by relist count", "by CVSG status", "Cert petitions by salience band", and the per-Term "Segment base rate by salience band (sal-v4)" table (pooled `elevated` bracketed `reached` figure over OT2017–OT2024 = 484.4/2810 ≈ 17.2%).

## CourtListener MCP

1. `search` type=o, q="Zavislak Netflix" — 0 results (the Ninth Circuit memorandum is not indexed as an opinion).
2. `call_endpoint dockets` id=73281629 — confirmed docket 25-1142, filed 2026-04-01, `date_terminated` null.
3. `search` type=o, q="Kelly Altria 1024(b)(4)", court=ca4, filed after 2026-07-01 — found *Richard Kelly v. Altria Client Services, LLC*, Nos. 25-1350 / 25-2080, published, decided 2026-08-10 (cluster 10945085, opinion 11412670).
4. `call_endpoint docket-entries` docket=73281629 — 0 entries (no post-snapshot movement visible on CourtListener).
5. `read_document` opinion_id=11412670, chunks 0, 3, 4 — Kelly's introduction and fiduciary section.
6. `read_document` opinion_id=11412670, chunks 5, 6 — Kelly's § 1024(b)(4) holding (Part IV) and footnote 8 aligning with *Premera* and *Mondry*.

## Other

- Downloaded petitioner's September 2, 2026 "Reply and Supplemental Brief" (4 pages) from the supremecourt.gov URL in the snapshot's docket entry and extracted its text with pypdf. Forward-mode retrieval of this case's own public filing; it is not provisioned by the pipeline. Used for the *Kelly* development.
- No web search was used.
