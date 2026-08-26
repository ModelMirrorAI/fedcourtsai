# Retrieval

## Base-rate context

- Read `metrics/statpack.md`, "The interim docket (applications)," and `metrics/statpack.json.interim`. Strictly prior OT2024 and OT2025 rows yielded 30 substantive grants among 226 resolved substantive applications. No `fedcourts query` or `open-events` call was made.

## CourtListener MCP

All searches were limited to pre-disposition lower-court material; no search sought this Supreme Court application's outcome. Parallel read-only checks repeated several searches, which are grouped below.

- `search(type="r", court=["ca7"], docket_number="26-2577")` — no result (query `90739e1e`; independent repeats also returned none).
- `search(type="r", party_name="Katherine Hobbins Forester")` — returned E.D. Wis. dockets 2:26-cv-01287 and 2:26-cv-00212 (query `9d318f28`; parallel queries `26c0970b` and related exact-name checks reached the same records).
- `get_endpoint_item(endpoint_id="dockets", item_id=73658638)` — metadata for *Hobbins Forester v. Gerol*, including the Section 2241 cause and July 22 filing date.
- `get_endpoint_schema(endpoint_id="docket-entries")` — field schema used to restrict the docket-entry request; one independent check also read the `recap-documents` schema.
- `call_endpoint(endpoint_id="docket-entries", docket=73658638, order_by="entry_number")` — 21 entries, including the full July 28 dismissal order (query `11f4acb6`; parallel successful queries `fd1b679b` and an unnumbered repeat). Two earlier parallel retries were throttled.
- `search(type="r", court=["ca7"], party_name="Katherine Hobbins Forester")` — no result (query `522c1391`; parallel query `47be58a3` and exact/broad name variants also returned none).
- `search(type="r", q="\"Hobbins Forester\" Gerol")` — returned only the E.D. Wis. habeas docket (query `f1e0ff0f`).
- `call_endpoint(endpoint_id="docket-entries", docket=72250320)` — two entries and the text of the related February 2026 civil complaint (query `e27a1281`; parallel query `dfb0e9ed`).
- Parallel lower-court searches for E.D. Wis. docket 2:26-cv-01287, party Adam Gerol, and attorney Katherine Hobbins Forester identified the same habeas docket and related civil action. Exact searches for Supreme Court docket text were not used substantively and returned no result.
- `search(type="o", court=["ca7"], case_name="Hobbins Forester", filed_after="2026-07-28", filed_before="2026-08-26")` — throttled with HTTP 429; parallel CA7 opinion searches returned no result.

No web search was used.
