# Retrieval log

Mode: `forward` (unrestricted). All material consulted predates the 2026-09-30 snapshot; the petition is set for the October 16, 2026 conference and has no disposition yet.

## Corpus (`fedcourts`, read-only via the cell's corpus service)

1. `uv run fedcourts paths --court scotus --docket 9026000005 --event evt-petition-disposition --role predictor` (no transfer line).
2. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 8`
   `ranged corpus reads: 11 GET(s), 2752512 byte(s)` — returned recent OT2025/OT2026 grants, mostly substantive applications with the SG as a party; no removal-power cert petitions surfaced, so I used it only as a sanity check on the granted population's shape.
3. `uv run fedcourts query --court scotus --citation '591 U.S. 197' --citation '594 U.S. 220' --citation '561 U.S. 477' --limit 5`
   `ranged corpus reads: 9 GET(s), 2359296 byte(s)` — empty; the tool printed its `note:` that only about 200 SCOTUS rows carry any reporter citation, so this is a coverage gap, not absence of the cases.

## Statpack (committed `metrics/statpack.md`)

Sections read: Modern discretionary-cert petitions by disposition; Modern cert petitions by originating circuit (CADC row); Cert petitions by relist count and by CVSG status (paid scored segment); SCOTUS cert petitions by Term; Segment base rate by salience band (sal-v4), pooled `elevated` bracketed `reached` over OT2017–OT2025.

## CourtListener MCP

1. `search` (type `o`, court `scotus`, filed after 2026-05-01, q: "Trump v. Slaughter" Humphrey's Executor overruled) — found cluster 10881681, opinion 11349203, Trump v. Slaughter, No. 25-332, decided 2026-06-29; also Trump v. Cook, 25A312, same day.
2. `search` (type `d`, court `scotus`, docket_number 25-1110, q: Harris v. Bessent) — 0 results.
3. `read_document` (opinion 11349203, chunks 0–1) — "No text is available for this document."
4. `search_document` (opinion 11349203, "adjudicat") — no text available.
5. `search_document` (opinion 11349203, "reinstate") — no text available.
6. `search` (type `d`, court `scotus`, q: Harris Bessent Merit Systems Protection Board) — 0 results.
7. `get_endpoint_item` (opinions, 11349203, fields plain_text) — returned the full slip opinion (about 227,000 characters). I read the syllabus and grepped for: adjudicat, National Labor, NLRB, Wiener, War Claims, reinstat, Federal Reserve, Article I, multimember, Harris, "no occasion today", "different set of questions", equitable relief, Held, and the lineup line. Key takeaways: Humphrey's overruled 6–3 (Roberts, C.J.; Thomas joining all but Part III-B; Gorsuch concurring; Sotomayor dissenting with Kagan and Jackson); in-house adjudication "is executive"; the Court reserved tenure protections for non-Article III courts and Federal Reserve-lineage bodies; the majority cited the district court's Wilcox opinion as an example of Humphrey's indeterminacy; the dissent named the NLRB and MSPB as open questions.

Total: 3 corpus commands (2 queries), 7 MCP calls. No web searches.
