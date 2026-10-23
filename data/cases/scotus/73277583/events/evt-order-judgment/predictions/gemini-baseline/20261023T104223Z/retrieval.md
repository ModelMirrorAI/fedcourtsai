# Retrieval Log (`retrieval.md`)

## 1. Corpus CLI Lookups (`fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "73277583" --event "evt-order-judgment" --role predictor`
   - Output: resolved `case_id` (`scotus/73277583`), `corpus` (`corpus/corpus.db`), and `event` (`data/cases/scotus/73277583/events/evt-order-judgment/event.yaml`).
2. `uv run fedcourts query --court scotus --limit 10 "Stinson Kisor Sentencing Guidelines commentary"`
   - CLI usage error (no free-text positional argument).
3. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 10`
   - Transfer line: `ranged corpus reads: 32 GET(s), 8388608 byte(s)`
   - Returned 10 recent 2020s granted SCOTUS rows.

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_get_endpoint_item` (`endpoint_id="dockets"`, `item_id=73277583`, `fields=["id", "case_name", "docket_number", "date_filed", "date_argued", "date_terminated"]`)
   - Confirmed `date_argued: "2026-10-13"` and `date_terminated: null`.
2. `mcp_courtlistener_call_endpoint` (`endpoint_id="docket-entries"`, `query={"docket": 73277583, "fields": ["id", "entry_number", "date_filed", "description"]}`)
   - Returned 0 RECAP docket entries (SCOTUS docket entries are not stored in RECAP).
3. `mcp_courtlistener_search` (`type="oa"`, `case_name="Beaird v. United States"`)
   - Located oral argument audio record `/audio/106844/kendrick-jarrell-beaird-v-united-states/` argued October 13, 2026.
4. `mcp_courtlistener_search` (`type="o"`, `q=""Stinson v. United States" "Kisor""`)
   - Retrieved appellate opinions addressing the *Stinson*/*Kisor* circuit split.
5. `mcp_courtlistener_get_endpoint_item` (`endpoint_id="audio"`, `item_id=106844`, `fields=["id", "case_name", "stt_status", "stt_transcript"]`)
   - Retrieved the full verbatim 104,491-character transcript of the October 13, 2026 oral argument before the Supreme Court.

## 3. Web Searches and Fetches

1. `google_web_search`: `"Beaird v. United States" "25-5343" "Stinson" Supreme Court`
2. `google_web_search`: `"Beaird v. United States" oral argument October 13 2026 SCOTUSblog OR Supreme Court`
3. `google_web_search`: `"Beaird v. United States" "Anthony Dick" OR "Eric Feigin" OR "Kevin Page" Supreme Court`
4. `google_web_search`: `"Beaird v. United States" "Stinson" "Kisor" "Eric J. Feigin" OR "Anthony J. Dick" brief vacatur OR affirmance`
5. `google_web_search`: `"Beaird v. United States" oral argument "Gorsuch" "Jackson" "Kavanaugh" "Barrett" "Roberts" "Alito" "Sotomayor" "Kagan" "Thomas"`
6. `google_web_search`: `"Beaird v. United States" "Feigin" oral argument Supreme Court October 13 2026`
7. `google_web_search`: `"Beaird v. United States" "Stinson" SCOTUSblog October 2026`
8. `google_web_search`: `"25-5343" "Brief for the United States" "Beaird" "affirm" OR "vacate" supremecourt.gov`
9. `google_web_search`: `"Anthony J. Dick" "25-5343" "Beaird" "appointed" supremecourt.gov`
10. `google_web_search`: `"No. 25-5343" "Kendrick Jarrell Beaird" "Brief for the United States" supremecourt.gov`
11. `google_web_search`: `"Anthony J. Dick" "invited to brief and argue" "25-5343"`
12. `google_web_search`: `"25-5343" "Brief for the United States" "The judgment of the court of appeals should be"`
13. `google_web_search`: `"Beaird" "25-5343" "judgment of the court of appeals should be affirmed" OR "judgment of the court of appeals should be vacated"`
14. `web_fetch`: `https://www.supremecourt.gov/docket/docketfiles/html/public/25-5343.html` (extracted post-April 20, 2026 merits briefing docket entries).
