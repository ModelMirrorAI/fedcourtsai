# Retrieval log — scotus/73500268, evt-petition-disposition, claude-baseline, run 20261003T200236Z

## Corpus tooling

1. `uv run fedcourts query --court scotus --disposition gvr --era 2020s`
   stderr: `ranged corpus reads: 45 GET(s), 11730944 byte(s)`
   Returned recent SCOTUS GVR priors (chiefly the June 29–30, 2026 cleanup GVRs: Monsanto v. Salas/Johnson/Anderson, Davis v. United States, Wells v. Texas, Lung'aho, Aquino, Harris, McMillan, Mbe, Beckford), read for the shape of GVR dockets (distribution counts 2–3, disposed on the first conference after the lead decision). Used as context only; no subject filter is available, so none is a judicial-estoppel prior.

## CourtListener MCP

2. `search` (type `o`, court `scotus`, q `Keathley "Buddy Ayers"`, filed after 2025-01-01) → one result: *Keathley v. Buddy Ayers Construction, Inc.*, No. 25-6, decided 2026-06-11, cluster 10873663.
3. `search` (type `o`, q `"judicial estoppel" "in light of Keathley"`, filed after 2026-06-01) → zero results.
4. `get_endpoint_item` (clusters, 10873663; fields case_name, date_filed, syllabus, judges, sub_opinions) → opinion id 11341134, author Jackson.
5. `read_document` (opinion 11341134, chunks 0–2 of 9) → syllabus and Parts I–II.A of the opinion: unanimous Court, vacated and remanded; held the Fifth Circuit's two-factor inadvertence rule erroneous and that courts must look to the totality of the circumstances; Thomas (joined by Gorsuch) and Sotomayor concurred.

## Committed base rates

- `metrics/statpack.md`: modern discretionary-cert disposition section, originating-circuit cut, relist-count and CVSG cuts (paid scored segment), salience-band section, per-Term table and the sal-v4 segment base rate by salience band table (pooled `elevated` bracketed `reached` over OT2017–OT2024).

## Not consulted

No web search. No search for this case's own docket, parties, or disposition.
