# Retrieval Log

## 1. Provisioned Case Record (`data/cases/scotus/9026000037/record/`)
- `record/context.json` — docket metadata, `band: "state"`, `cert_anchor` (`rate: 0.23333333333333334`, `lookback_terms: 10`), `amicus_briefs: null`, `snapshot_date: "2026-08-27"`.
- `record/snapshots/2026-08-27.json` — Supreme Court docket snapshot for No. 26-37 (*New Mexico v. Samuel Neal*), showing petition filed July 6, 2026, waiver filed August 18, 2026, and response requested August 26, 2026 (due September 25, 2026).
- `record/same-question.json` — confirmed zero companion or same-question petitions (`"petitions": []`).
- `record/documents/documents.json`, `record/documents/questions-presented.txt`, and `record/documents/petition.txt` — full text of New Mexico's Petition for a Writ of Certiorari and Appendices A–D, including the New Mexico Supreme Court's opinion in *State v. Neal*, 2026-NMSC-009 (filed March 9, 2026), and the New Mexico Court of Appeals' memorandum opinion in *State v. Neal*, No. A-1-CA-40205 (filed April 24, 2024).

## 2. Corpus Priors (`uv run fedcourts query`)
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
  - `ranged corpus reads: 33 GET(s), 8650752 byte(s)`
  - Retrieved recent 2020s granted SCOTUS priors (`scotus/9026000012`, `scotus/9026000204`, `scotus/73281386`, `scotus/73283862`, `scotus/73500246`, `scotus/73281619`, `scotus/73500251`, `scotus/9026000104`, etc.) to compare cert-stage structural indicators (amicus activity, originating court posture, distribution counts).
- `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 10`
  - `ranged corpus reads: 6 GET(s), 1572864 byte(s)`
  - Retrieved recent 2020s denied SCOTUS priors for baseline comparison.

## 3. CourtListener MCP Server Retrievals (Blinded to `< 2026-08-27`)
- `mcp_courtlistener_search` (`query_id="df43028c"`, `type="o"`, `court="scotus"`, `q="Blockburger Whalen"`, `filed_before="2026-08-27"`):
  - Located Supreme Court multiple-punishment and *Blockburger* precedents predating the August 27, 2026 cutoff, including:
    - *Barrett v. United States*, No. 24-5774, 607 U.S. ___ (decided Jan. 14, 2026) — CourtListener `cluster_id: 10774608`, `opinion_id: 11241193` (examined via `get_endpoint_item`, `search_document`, and `read_document` chunks `0, 4, 6, 8, 9, 10`). Confirmed that the Court recently reaffirmed *Whalen v. United States*, 445 U.S. 684 (1980), treating *Blockburger* in single-proceeding cumulative-punishment cases as a rule of statutory construction for discerning legislative intent, noted in footnote 10 that the analysis focused on the specific statutory clause of a multi-alternative statute under which the defendant was convicted, and included a partial concurrence by Justice Gorsuch discussing *Blockburger* in concurrent prosecutions.
    - *Whalen v. United States*, 445 U.S. 684 (1980) (`cluster_id: 110237`)
    - *Albernaz v. United States*, 450 U.S. 333 (1981) (`cluster_id: 110428`)
    - *Missouri v. Hunter*, 459 U.S. 359 (1983) (`cluster_id: 110824`)
    - *Illinois v. Vitale*, 447 U.S. 410 (1980) (`cluster_id: 110307`)
    - *United States v. Dixon*, 509 U.S. 688 (1993) (`cluster_id: 9135777`)
    - *Rutledge v. United States*, 517 U.S. 292 (1996) (`cluster_id: 118013`)
    - *Gamble v. United States*, 587 U.S. 678 (2019) (`cluster_id: 4630267`)
