# Retrieval log

## Corpus (`fedcourts`)

1. `uv run fedcourts paths --court scotus --docket 73500236 --event evt-petition-disposition --role predictor`
   (path resolution only; no transfer line printed).
2. `uv run fedcourts query --court scotus --citation "172 U.S. 269" --citation "239 U.S. 478" --citation "102 U.S. 294"`
   stderr: `ranged corpus reads: 1357 GET(s), 355663872 byte(s)`
   Result: no rows; the tool printed its coverage note that only 200 of 590,919 scotus rows carry citation data. Nothing used.
3. `uv run fedcourts query --court scotus --era 2020s --disposition granted`
   stderr: `ranged corpus reads: 20 GET(s), 5242880 byte(s)`
   Result: a ranked list of recent granted rows (mostly government-party petitions and substantive applications). Used only as a reminder of what recently granted dockets look like; no row was topically similar to a special-assessment / municipal-bond petition.

## CourtListener MCP

1. `search(type="o", q='"Marin Metropolitan District" Bondshares')` — returned the earlier Landmark Towers Ass'n v. UMB Bank line of Colorado decisions (Colo. App. 2014, 2016, 2018; Colo. 2017) involving the same district. Confirms the prior litigation the petition describes. The unpublished June 12, 2025 Colorado Court of Appeals opinion in this case did not surface.
2. `search(type="d", court="scotus", docket_number="25-1334")` — no results; the Supreme Court docket is not in RECAP. No post-snapshot docket entries were seen.

## Web searches

None.

## Committed base rates

`metrics/statpack.md`: "Modern discretionary-cert petitions by disposition", "Cert petitions by relist count (paid scored segment)", "Cert petitions by CVSG status (paid scored segment)", "Cert petitions by salience band", "SCOTUS cert petitions by Term", and "Segment base rate by salience band (sal-v4)" (baseline column, Terms 2017–2024 pooled by n).
