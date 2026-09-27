# Retrieval log

Beyond the provisioned snapshot, `context.json`, the two provisioned documents
(`petition.txt`, `questions-presented.txt`) and the committed
`metrics/statpack.md`:

## Corpus CLI (`fedcourts query`, corpus service backend)

1. `uv run fedcourts query --court scotus --citation "146 S. Ct. 1497" --limit 3`
   — no rows; CLI note: citation column sparse (200 scotus rows carry any cite).
   `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   — 5 recent granted rows (2025 substantive applications); used only to confirm
   the row schema, not as priors.
   `ranged corpus reads: 10 GET(s), 2490368 byte(s)`
3. `uv run fedcourts query --court scotus --era 2020s --limit 400` — scanned
   case names for Whittaker / Atlas Turner / Protopapas / Altrad / Charter;
   no matches in the returned 400.
   `ranged corpus reads: 37 GET(s), 9699328 byte(s)`
4. `uv run fedcourts query --court scotus --era 2020s --include-open --limit 1500`
   — refused (limit must be ≤ 500); read nothing.
5. `uv run fedcourts query --court scotus --era 2020s --include-open --limit 500`
   — same name scan, 500 rows, no matches.
   `ranged corpus reads: 1 GET(s), 262144 byte(s)`

## CourtListener MCP

1. `call_endpoint dockets` (court scotus, docket_number 26-350) — 0 results.
2. `search` (type o, court sc, "Protopapas receiver Cape Charter Consolidated")
   — 1 result: *John A. Tibbs v. 3M Company*, cluster 10864763, filed
   2026-05-27, docket 2025-002104 (the decision below).
3. `call_endpoint dockets` with `__startswith` / `__icontains` filters —
   validation error; read nothing.
4. `search` (type o, "Whittaker Clark" receiver Protopapas) — 3 results: two
   CA3 *Whittaker Clark & Daniels* clusters (2025-09-10, 2026-04-27) and the
   SC *Tibbs* cluster.
5. `call_endpoint dockets` (scotus, 26-159) — 0 results.
6. `call_endpoint dockets` (scotus, 26-263) — 0 results.
7. `search` (type d, scotus, Protopapas OR Whittaker OR Altrad) — 0 results.
8. `search` (type o, scotus, "Atlas Turner" Welch) — 0 results.
9. `search` (type d, scotus, filed after 2026-07-01, Whittaker) — 0 results.
10. `search` (type d, scotus, "Atlas Turner") — 0 results.
11. `get_endpoint_item clusters 10864763` — decision below; syllabus lists the
    five questions the state court granted certiorari on; single sub-opinion.
12. `search_document` (opinion 11332208, "dissent") — 0 matches (decision below
    appears unanimous).

## Web (engine search / fetch)

1. WebSearch: Whittaker Clark & Daniels cert petitions 26-159 / 26-263 —
   surfaced the 26A86 extension application, a HarrisMartin article on the
   talc claimants' August 25 petition, and CA3 opinion links.
2. WebSearch: Altrad / Cape Intermediate Holdings / 26-350 — surfaced
   FITSNews (June 12, 2026) on the state rehearing petitions and English High
   Court judgments (Cape Intermediate Holdings v. Protopapas; Altrad v.
   Protopapas).
3. WebSearch: Atlas Turner v. Welch cert denied — surfaced docket 25-213
   filings and a Legal Newsline headline; its summary attributed a Kavanaugh
   "would grant" to 25-213, which the order list below shows was wrong.
4. WebSearch: Whittaker petitions' response / conference status — nothing new.
5. WebSearch: "25-213" order list — surfaced the January 12, 2026 order list.
6. WebFetch supremecourt.gov docket 25-213 — full entry list (filed
   2025-08-18; waivers; three amici 2025-09-22; distributed 10/17/2025;
   Response Requested 2025-10-08; BIOs 2025-12-08; reply 2025-12-19;
   distributed 1/9/2026; denied 2026-01-12, Alito took no part).
7. WebFetch supremecourt.gov docket 26-159 — Protopapas v. Whittaker Clark &
   Daniels; filed 2026-07-24, docketed 2026-08-03, BIO 2026-08-25, reply
   2026-09-04.
8. WebFetch supremecourt.gov docket 26-263 — Official Committee of Talc
   Claimants v. Whittaker; filed 2026-08-25, docketed 2026-09-08, response
   extended to 2026-11-06.
9. WebFetch supremecourt.gov docket 26-350 — Altrad Investment Authority v.
   Cape Intermediate Holdings; Shanmugam counsel; filed 2026-09-08, docketed
   2026-09-15, response due 2026-10-15; Vide 26-328.
10. WebFetch supremecourt.gov docket 26-328 (this case) — only the 2026-09-08
    filing entry; no later entries.
11. WebFetch January 12, 2026 order list PDF (011226zor_3d9g.pdf) — text
    extracted locally; 25-213 entry reads "denied. Justice Alito took no
    part"; the Kavanaugh would-grant notation belongs to 24-1062 (Hertz).

No lookup of this case's disposition was made and none exists.
