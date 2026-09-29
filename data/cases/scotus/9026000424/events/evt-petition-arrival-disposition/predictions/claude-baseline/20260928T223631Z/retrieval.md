# Retrieval log

## Corpus lookups (`fedcourts`)

1. `uv run fedcourts query --court scotus --era 2020s` (default limit) — probe of
   the query surface and row shape.
   `ranged corpus reads: 9 GET(s), 2228224 byte(s)`
2. `uv run fedcourts query --court scotus --era 2020s --limit 400` — scanned
   captions for "District Court" (mandamus-style captions): 3 hits (26A256,
   25-7266, 25-7229), all `denied`. Disposition mix of the pull: 343 denied,
   28 gvr, 21 granted, 6 dismissed, 2 withdrawn.
   `ranged corpus reads: 40 GET(s), 10485760 byte(s)`

Base rates: the committed `metrics/statpack.md` — "Modern discretionary-cert
petitions by disposition", "by originating circuit" (ca4 row), "by relist
count", "by CVSG status", "Segment base rate by salience band (sal-v4)"
(baseline column pooled over OT2017–OT2025).

## CourtListener MCP lookups

1. `search` type=r, q="Boddie", court=[ca4, mdd], newest first — found
   D. Md. 1:26-cv-00214 "Boddie v. Warden" (Griggsby) and unrelated Boddie
   rows.
2. `search` type=o, q="Boddie", court=ca4, filed after 2025-06-01 — no
   relevant opinion.
3. `search` type=d, q="Boddie", court=scotus — 0 results.
4. `call_endpoint` docket-entries, docket=72187846 (Boddie v. Warden) — 0
   entries mirrored.
5. `search` type=d, docket_number="26-1130", court=ca4 — "In re: Beckie
   Boddie", docket_id 72251389.
6. `search` type=o, q="Boddie" mandamus, court=[ca4, mdd] — 0 results.
7. `search` type=o, case_name="Boddie", court=mdd, filed after 2026-01-01 — 0
   results.
8. `call_endpoint` docket-entries, docket=72251389 — entries dated 2026-02-09
   and 2026-04-09 (two).
9. `get_endpoint_item` dockets/72251389 — first attempt failed on an invalid
   field name; second attempt returned originating case D. Md.
   1:18-cv-03309-PX, last filing 2026-04-09.
10. `get_endpoint_item` dockets/72187846 — Boddie v. Warden metadata (no
    nature of suit recorded).
11. `search` type=o, docket_number="26-1130", court=ca4 — 0 results (the
    unpublished per curiam is not in the opinion index).
12. `search` type=d, case_name="Boddie", court=ca4, filed after 2025-01-01 —
    0 results.
13. `search` type=d, docket_number="1:18-cv-03309", court=mdd — "In re
    Sanctuary Belize Litigation" (Xinis), FTC Act cause, docket_id 14527299.
14. `search` type=r, q="Boddie", docket_number="1:18-cv-03309", court=mdd —
    three entries filed by Beckie Boddie: DE 1540 (2024-10-28, "Petition:
    Right of Victim as Third Party to Petition the Court"), DE 1606 and DE 1607
    (2026-01-20, correspondence).
15. `search` type=rd, q="Boddie", docket_number="26-1130", court=ca4 — three
    CA4 entries: informal briefing order (2026-02-09), judgment order and
    unpublished per curiam opinion (2026-04-09). Documents not available to
    read.

No web searches. Nothing about this petition's own disposition was sought or
surfaced; the case is pending.
