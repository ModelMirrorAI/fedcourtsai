# Retrieval Log — `scotus/9026000604` (`evt-petition-disposition`)

Mode: `forward` (`DECIDED_BEFORE` unset; `REPLAY_CUTOFF` unset). No lookup targeted the disposition, subsequent history, or external forecasts of `scotus/9026000604` (*Daniel Samuel Eta v. United States*, No. 26-604). No web searches were executed.

## 1. `fedcourts` CLI Calls

1. Path check and CLI help inspection:
   - `uv run fedcourts paths --court "scotus" --docket "9026000604" --event "evt-petition-disposition" --role predictor`
   - `uv run fedcourts query --help`
   - Returned cell paths and CLI flag documentation (no corpus reads).

2. Initial attempted party-filter calls (rejected by CLI argument parser — `--party` is not a valid option on `fedcourts query`):
   - `uv run fedcourts query --corpus-backend ranged --court scotus --party "Anibowei" --exclude-case "scotus/9026000604" --limit 10`
     - Result: CLI usage error (`No such option: --party`); no corpus reads.
   - `uv run fedcourts query --corpus-backend ranged --court scotus --party "Cardozo" --era 2020s --exclude-case "scotus/9026000604" --limit 10`
     - Result: Not reached after preceding error; no corpus reads.

3. Companion / same-issue petitions and linked extension application (via default `FEDCOURTS_CORPUS_BACKEND=service`):
   - `uv run fedcourts query --court scotus --docket-number 26-208 --include-open`
     - `ranged corpus reads: 21 GET(s), 5505024 byte(s)`
     - Returned open row `scotus/9026000208` (*George Anibowei v. Todd Blanche, Attorney General, et al.*, No. 26-208, filed `2026-08-19`, `distributed_for_conference: "2026-10-09"`, `distribution_count: 1`, `disposition: null`, `last_live_polled: "2026-11-22"`, 10 amicus curiae counsel entries).
   - `uv run fedcourts query --court scotus --docket-number 26-6011 --include-open`
     - `ranged corpus reads: 1 GET(s), 262144 byte(s)` (part of same shell invocation; verified IFP border-search petition *Belmonte Cardozo v. United States*, No. 26-6011).
   - `uv run fedcourts query --court scotus --docket-number 26A320 --include-open --include-applications`
     - Checked mistyped application number before reading full `Links` string from `2026-11-25.json` (`26A383`).
   - `uv run fedcourts query --court scotus --docket-number 26A383 --include-open --include-applications`
     - `ranged corpus reads: 1 GET(s), 262144 byte(s)`
     - Returned `scotus/9526000383` (*Daniel Samuel Eta v. United States*, No. 26A383, routine time-extension application granted by Justice Barrett on `2026-09-23`).

4. Prior SCOTUS digital-privacy and border-phone-search petitions:
   - `uv run fedcourts query --court scotus --docket-number 25-112 --include-open`
     - `ranged corpus reads: 1 GET(s), 262144 byte(s)`
     - Returned `scotus/9025000112` (*Chatrie v. United States*, No. 25-112, geofence-warrant Fourth Amendment merits case).
   - `uv run fedcourts query --court scotus --docket-number 20-1505 --include-open`
     - `ranged corpus reads: 1 GET(s), 262144 byte(s)`
     - Returned prior civil border-device-search cert petition *Merchant v. Mayorkas*, No. 20-1505 (cert. denied June 28, 2021).
   - `uv run fedcourts query --court scotus --docket-number 20-1043 --include-open`
     - `ranged corpus reads: 1 GET(s), 262144 byte(s)`
     - Returned `scotus/72465054` (*United States v. Miguel Angel Cano*, No. 20-1043, Solicitor General cert petition from 9th Cir. border cell-phone search decision, `disposition: "denied"` on `2021-06-28` after `distribution_count: 2`).

## 2. CourtListener MCP Calls

1. `mcp_courtlistener_search` (`type="o"`, `case_name="Anibowei"`, `num_results=10`):
   - Returned 1 published opinion: *Anibowei v. Morgan*, 70 F.4th 898 (5th Cir. 2023) (`cluster_id=9407482`, `docketNumber="20-10059"`).
2. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `q=""Mendez v. United States" OR "Alasaad v." OR "Cano v. United States" OR "Wanjiku v. United States" OR "Pulido v. United States" OR "Nkongho v. United States" OR "Aigbekaen v. United States""`, `num_results=20`):
   - Returned 190 historical SCOTUS cert-order clusters matching unrelated/older defendants with shared surnames (*Pulido*, *Mendez*, *Cano*).
3. `mcp_courtlistener_search` (`type="o"`, `court="ca5"`, `docket_number="24-11042"`, `num_results=5`):
   - Returned 0 indexed opinions under `24-11042`.
4. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `filed_after="2020-01-01"`, `q=""Alasaad" OR "Cano" OR "Xiang" OR "Aigbekaen" OR "Nkongho" OR "Karpov" OR "Mendez" "border""`, `num_results=20`):
   - Returned 103 general SCOTUS opinions mentioning `"border"` (e.g., *Mullin v. Al Otro Lado*, *Egbert v. Boule*, *Biden v. Texas*); no cert-stage separate writings in those border-phone-search dockets.
5. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `docket_number="25-112"`, `num_results=5`):
   - Returned 1 cluster: *Chatrie v. United States*, No. 25-112, decided `2026-06-29` (`cluster_id=10881683`, majority by Justice Kagan).
6. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `docket_number="20-1505"`, `num_results=5`):
   - Returned 0 opinion clusters.
7. `mcp_courtlistener_search` (`type="d"`, `court="scotus"`, `docket_number="26-208"`, `num_results=5`):
   - Returned 0 RECAP docket entries.
8. `mcp_courtlistener_search` (`type="o"`, `court="scotus"`, `filed_after="2024-06-01"`, `q=""Mendez v. United States" OR "Pulido v. United States" OR "Nkongho v. United States" OR "Castillo v. United States" OR "Xiang v. United States""`, `num_results=20`):
   - Returned 0 SCOTUS opinion clusters (confirming no separate writings or merits opinions in those recent border-device-search petitions).
9. `mcp_courtlistener_get_endpoint_item` (`endpoint_id="clusters"`, `item_id=10881683`):
   - Retrieved metadata for *Chatrie v. United States* (`sub_opinions: [".../opinions/11349205/"]`, `date_filed: "2026-06-29"`).
10. `mcp_courtlistener_read_document` (`opinion_id=11349205`, `chunk_index=0`, `chunk_size=8000`):
    - Read syllabus chunk of *Chatrie v. United States* (OT2025, No. 25-112) for background Fourth Amendment digital-search context.
