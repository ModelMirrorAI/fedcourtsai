## Provisioned case documents

- `data/cases/scotus/9026000019/record/context.json` — verified cell metadata (`band: baseline`, `salience_version: sal-v4`, `distribution_count: 1`, `mode: forward`, `snapshot_date: 2026-09-09`, `cutoff: 2026-09-10`).
- `data/cases/scotus/9026000019/record/snapshots/2026-09-09.json` — docket snapshot showing the petition filed June 29, 2026, distributed August 19, 2026 for the September 28, 2026 conference, and the September 9, 2026 call for a response due October 9, 2026.
- `data/cases/scotus/9026000019/record/documents/documents.json` — manifest of provisioned filings.
- `data/cases/scotus/9026000019/record/documents/questions-presented.txt` — Question Presented text.
- `data/cases/scotus/9026000019/record/documents/petition.txt` — Petition for a Writ of Certiorari filed June 29, 2026.
- `data/cases/scotus/9026000019/record/documents/appendix.txt` — Appendix to the Petition, including the January 28, 2026 opinion of the Fifth Circuit Court of Appeal of Louisiana (`25-K-572`, App. 1a–21a), the May 12, 2026 writ denial by the Supreme Court of Louisiana (`2026-KK-00308`, App. 22a), the July 11, 2025 and May 14, 2025 trial court orders (App. 23a–42a), and the June 13, 2025 pretrial supervisory writ denial by the Fifth Circuit Court of Appeal of Louisiana (`25-K-267`, App. 43a–49a).

## Corpus queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --citation "489 U.S. 538" --citation "391 U.S. 145" --limit 10`
   - Transfer line: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Returned 0 rows (citation column holds parallel cites of the case itself rather than cited authorities).
2. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 10`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 10 recent 2020s SCOTUS denied dispositions (including dockets where a response was requested and later denied, such as `scotus/9526000499` and `scotus/9526000416`).
3. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer line: `ranged corpus reads: 31 GET(s), 8060928 byte(s)`
   - Returned 10 recent 2020s SCOTUS granted dispositions (including cert grants such as `scotus/9026000012`, `scotus/9026000204`, `scotus/73500251`, and `scotus/9026000104`), providing comparative context on the salience, counsel, and amicus profile of granted petitions.

## External retrieval (CourtListener MCP)

- `mcp_courtlistener_search` and `mcp_courtlistener_read_document` (`opinion_id: 5133431`): Retrieved and read *Andersen v. Eighth Judicial District Court*, 135 Nev. 321, 448 P.3d 1120 (2019 NV 42), confirming that the Nevada Supreme Court held Nevada's state-law firearm prohibition elevated first-offense misdemeanor domestic battery (6-month maximum jail term) to a "serious" offense requiring a jury trial under *Blanton v. City of North Las Vegas*, 489 U.S. 538 (1989), distinguishing its earlier decision on federal collateral consequences in *Amezcua v. Eighth Judicial District Court*, 130 Nev. 45, 319 P.3d 602 (2014), *cert. denied*, 135 S. Ct. 59 (2014).
- `mcp_courtlistener_search` and `mcp_courtlistener_read_document` (`opinion_id: 11155132`): Retrieved and read *People v. Suazo*, 32 N.Y.3d 491, 118 N.E.3d 168 (2018), holding that federal deportation consequences trigger a Sixth Amendment jury-trial right for a class B misdemeanor.
- `mcp_courtlistener_search` and `mcp_courtlistener_read_document` (`opinion_id: 7125493`, `opinion_id: 1198152`, `opinion_id: 74349`): Retrieved and read *State v. Woolverton*, 52 Kan. App. 2d 700, 371 P.3d 941 (2016), *State ex rel. McDougall v. Strohson*, 190 Ariz. 120, 945 P.2d 1251 (1997), and *United States v. Chavez*, 204 F.3d 1305 (11th Cir. 2000), confirming the broader consensus that 18 U.S.C. § 922(g)(9) and collateral firearm restrictions do not convert a presumptively petty six-month misdemeanor into a serious offense under *Blanton*.
