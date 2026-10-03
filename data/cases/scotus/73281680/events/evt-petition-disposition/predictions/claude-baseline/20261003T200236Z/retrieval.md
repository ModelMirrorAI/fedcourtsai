# Retrieval log

Mode: `forward` (pending petition; conference of 10/9/2026 not yet held). No
material about this petition's own disposition exists or was sought.

## Corpus tooling
- `uv run fedcourts paths --court scotus --docket 73281680 --event evt-petition-disposition --role predictor`
- `uv run fedcourts query --court scotus --era 2020s --limit 8` →
  `ranged corpus reads: 6 GET(s), 1572864 byte(s)` (recent SCOTUS priors; shape only, no close analogue)
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 6` →
  `ranged corpus reads: 2 GET(s), 524288 byte(s)` (recent grants; none comparable)
- Committed `metrics/statpack.md`: modern cert by disposition, by originating
  circuit, relist-count cut, CVSG cut, per-Term table, segment base rate by
  salience band (sal-v4).

## CourtListener MCP
- `search` (opinions, ca8, "Fofana", filed after 2025-06-01) → *Abrahim Fofana v. Kristi Noem*, No. 24-2485, cluster 10772463, opinion 11239048.
- `search` (RECAP, ca8, docket 24-2485) → no results.
- `read_document` opinion 11239048 → full text of the Eighth Circuit opinion (Jan. 9, 2026).
- `search` (opinions, several circuit-split formulations with a court list) → empty (the multi-court filter returned nothing).
- `search_document` opinion 10757634 (*Bouarfa*) for "1159" → none; for "need not" → the reservation at 604 U.S. 19.
- `search` (opinions, "1252(a)(2)(B)(ii)" AND "threshold" AND Bouarfa, after 2024-12-10) → Geda (3d Cir.), Ortez Reyes (4th Cir.), Mukantagara (10th Cir.), Chairez and Ruiz (9th Cir.), two D.D.C. opinions, Qatanani (3d Cir.).
- `search` (opinions, "1159" AND "1252(a)(2)(B)(ii)" AND Patel AND "adjustment of status", after 2022-05-16) → Shaiban v. Jaddou (4th Cir. 2024, opinion 9957696), Fofana, Mukantagara, others.
- `search_document` opinions [11239815, 9957696, 11271786, 11271054, 10786455] for "threshold" and for "1159" → Shaiban and Fofana hold clause (ii) bars review of § 1159(b) eligibility; Mukantagara (Jan. 2026) held the opposite relying on *Hosseini* (6th Cir. 2016); Ortez Reyes distinguishes Shaiban.
- `search` (dockets, scotus, Shaiban OR Mukantagara OR Hosseini) → no results.

## Web
- WebFetch https://www.supremecourt.gov/docket/docketfiles/html/public/25-1154.html (twice: entries/links; verbatim counsel blocks) → same 12 entries as the snapshot; petitioner listed as his own counsel of record at a Minneapolis firm address; only one linked PDF (4th extension letter); no petition or BIO PDF.
- curl + pypdf: the 4th extension letter (press-of-business ground; petitioner's counsel did not oppose).
- WebSearch "Fofana" "25-1154" … → nothing case-specific beyond the Eighth Circuit PDF.
- WebSearch "Fofana v. Mullin" OR "Fofana v. Noem" brief in opposition … → nothing on this petition.
- WebFetch https://www.ca10.uscourts.gov/sites/ca10/files/opinions/010110793946.pdf → unrelated 10th Cir. *Aly Issac Fofana* order (2023); discarded.
- WebFetch justice.gov OSG brief search → HTTP 403.
- WebSearch "Mukantagara" … → Tenth Circuit vacated its January 2026 judgment on panel rehearing (July 2026) after *Mullin v. Doe*; supplemental briefing ordered.
- WebSearch "Shaiban v. Jaddou" certiorari → No. 24-183; SG memorandum (Nov. 2024) asking for a hold pending *Bouarfa*; cert denied on the January 13, 2025 order list.
- curl + pypdf https://justice.gov/osg/media/1390131/dl?inline= → SG memorandum in No. 24-183 (read in full). The ca10 PDF 010111468891 download returned HTML, not read.
- WebFetch https://www.sabrinadamast.com/… (July 31, 2026 post) → summary of the Mukantagara rehearing order.
- WebFetch https://en.wikipedia.org/wiki/Mullin_v._Doe → QP, holding (TPS statute bars non-constitutional review), 6–3, Alito, June 25, 2026.

Roughly 25 retrieval calls in total; budget respected.
