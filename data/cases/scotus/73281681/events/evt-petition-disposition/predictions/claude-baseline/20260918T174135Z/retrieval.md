# Retrieval log

## Corpus (`fedcourts query`, via the cell's corpus backend)
- `uv run fedcourts query --court scotus --citation "601 U.S. 267"` → `ranged corpus reads: 10 GET(s), 2555904 byte(s)`; no rows (note: citation column populated on ~200 scotus rows only).
- `uv run fedcourts query --court scotus --citation "570 U.S. 595"` → `ranged corpus reads: 0 GET(s), 0 byte(s)`; no rows (same note).
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8` → `ranged corpus reads: 27 GET(s), 7077888 byte(s)`; 8 rows (four 26A emergency applications, then 25-246 Jouppi, 25-238 Viramontes, 25-566 Grant, 25-965 Grand). Used only as a sanity check on the corpus's granted population; not informative for this question.
- Statpack: `metrics/statpack.md` — modern cert by disposition, relist-count cut, CVSG cut, salience-band cut, per-Term table, and the `sal-v4` segment band table (pooled `elevated` reached, OT2017–OT2024).

## CourtListener MCP
- `search(type=d, court=scotus, docket_number=25-958)` → 0 results.
- `search(type=d, court=scotus, docket_number=25-1187)` → 0 results.
- `call_endpoint(dockets, court=scotus, docket_number=25-958)` → docket id 73280999, *George Sheetz v. County of El Dorado*, filed 2026-02-11, not terminated in CL.
- `get_endpoint_item(dockets, 73281681)` → this docket; `date_modified` 2026-08-19, `date_terminated` null.
- `call_endpoint(docket-entries, docket=73280999)` → 0 entries (CL holds none for that docket).
- `search(type=o, q='Koontz "in lieu" "monetary exaction" Nollan Dolan', filed_after=2024-04-12)` → 2 results: the decision below (N.Y. Ct. App., 2026-01-13) and *Sheetz v. County of El Dorado* (Cal. Ct. App., 2025-07-29). No new federal appellate authority surfaced.

## Web fetches (supremecourt.gov public docket feed)
- `https://www.supremecourt.gov/rss/cases/JSON/25-958.json` — Sheetz II docket: waiver Feb 20; distributed for 3/20; **Response Requested Mar 2**; BIO May 11; reply May 21; distributed for 6/11; **Petition DENIED June 15, 2026** (no separate writing noted in the entry). Predates my snapshot; used as forward signal, disclosed in `flags.json`.
- `https://www.supremecourt.gov/rss/cases/JSON/25-1187.json` — this docket; confirmed the entry list matches the snapshot and no entry postdates Aug 19, 2026; obtained the reply-brief URL.
- `https://www.supremecourt.gov/DocketPDF/25/25-1187/419218/20260817115638248_FINAL%20SoHo%20NoHo%20reply%20pdfa.pdf` — petitioners' reply (12 pp.), text extracted locally with pypdf and read in full.

No other web searches.
