# Retrieval log

Mode: `forward`. Nothing retrieved concerned this petition's own disposition;
as of the 2026-10-05 snapshot the BIO is due Oct. 30, 2026 and no conference
has considered the petition.

## Corpus tooling

- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 12`
  stderr: `ranged corpus reads: 28 GET(s), 7208960 byte(s)`
  Returned 12 recent granted SCOTUS rows, mostly 2025–2026 substantive
  applications and federal-petitioner grants; no subject filter isolates
  religious-liberty cert petitions, so these did not shape the forecast.
- Base rates: the committed `metrics/statpack.md`, sections "Modern
  discretionary-cert petitions by disposition", "Modern cert petitions by
  originating circuit", "Cert petitions by relist count (paid scored
  segment)", "Cert petitions by CVSG status (paid scored segment)", and
  "Segment base rate by salience band (sal-v4)" (pooled baseline `reached`
  rate over Terms 2017–2025).

## CourtListener MCP (9 calls)

1. `search` opinions, court ca5, q `Perez "City of San Antonio" Brackenridge cormorant`, filed after 2024-01-01: four Fifth Circuit opinions in No. 23-50746 (2024-04-11, 98 F.4th 586; 2024-08-28, 115 F.4th 422; 2025-08-13; 2025-12-12, cluster 10754683).
2. `search` opinions, court scotus, q `"Apache Stronghold" certiorari denied Gorsuch dissenting`, filed after 2025-01-01: no results.
3. `get_endpoint_item` clusters 10754683: sub-opinion 11221268, no syllabus.
4. `search` opinions, court ca5, q `Perez "City of San Antonio" rehearing en banc Oldham`, filed after 2026-01-01: no results (the Feb. 27, 2026 en banc denial order is not indexed; I relied on the petition's account of it).
5. `search` opinions, court scotus, q `"Apache Stronghold"`, filed after 2025-01-01: no results.
6. `search` dockets, court scotus, q `"Apache Stronghold"`: no results.
7. `read_document` opinion 11221268, chunks 0–1 of 15 (7000 chars each): the panel (Stewart, J., with Richman; Higginson dissenting) withdrew its August 2025 opinion after the Texas Supreme Court answered the certified question and again affirmed; factual and procedural background.
8. `search` opinions, court ca9, q `"Apache Stronghold" "Oak Flat" en banc substantial burden`, filed after 2024-01-01: the Ninth Circuit en banc opinions of 2024-03-01 (95 F.4th 608) and 2024-05-14, plus two 2026 San Carlos Apache Tribe opinions; none opened.
9. `read_document` opinion 11221268, chunks 5–9 of 15: the substantial-burden holding (framed under Texas RFRA and Barr v. City of Sinton, on the preliminary-injunction record), the compelling-interest discussion, and the least-restrictive-means analysis including the City's dispute of the "never studied alternatives" admission.


## Web searches

None.
