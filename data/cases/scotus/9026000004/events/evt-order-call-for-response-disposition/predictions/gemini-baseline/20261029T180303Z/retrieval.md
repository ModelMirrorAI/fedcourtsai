# Retrieval Log: *Samsung Electronics America, Inc. v. Jordan Brewer* (No. 26-4)

**Predictor:** `gemini-baseline`  
**Run ID:** `20261029T180303Z`  
**Event:** `evt-order-call-for-response-disposition`  
**Cutoff Date:** `2026-08-15` (Snapshot `2026-08-14.json`)

---

## 1. Corpus Queries (`uv run fedcourts query`)

1. **Command:** `uv run fedcourts query --court scotus --citation "600 U.S. 122" --limit 10`
   - **Transfer stderr line:** `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - **Result:** 0 rows returned (`note:` explained that `citations` holds a case's own parallel cites on SCOTUS rows rather than a citing-cases graph).

2. **Command:** `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 10`
   - **Transfer stderr line:** `ranged corpus reads: 31 GET(s), 7929856 byte(s)`
   - **Result:** Returned 10 recent OT2026/OT2025 granted SCOTUS dockets (`scotus/9526000512`, `scotus/9026000012`, `scotus/9026000204`, `scotus/9526000476`, `scotus/73281386`, `scotus/73283862`, `scotus/73500246`, `scotus/73281619`, `scotus/73500251`, `scotus/9026000104`), used to compare recent granted petition trajectories against No. 26-4's `baseline` posture.

3. **Command:** `uv run fedcourts query --court scotus --era 2020s --limit 20 | grep -i -E "Mallory|jurisdiction|Georgia|Samsung|Cooper Tire" || true`
   - **Transfer stderr line:** `ranged corpus reads: 0 GET(s), 0 byte(s)` (served from warm local corpus service cache)
   - **Result:** No matching companion or related Georgia personal-jurisdiction petitions in the top 20 recent rows.

---

## 2. CourtListener MCP Calls

1. **Tool:** `mcp_courtlistener_search`
   - **Parameters:** `{"type": "o", "q": ""Mallory v. Norfolk Southern" "Cooper Tire" "general jurisdiction""}`
   - **Result:** Failed with `Rate limit exceeded: HTTP 429: {'detail': 'Request was throttled. Rate limit exceeded: 1400/day. Expected available in 2185 seconds.'}`.

2. **Tool:** `mcp_courtlistener_search`
   - **Parameters:** `{"type": "o", "case_name": "Brewer v. Samsung Electronics America"}`
   - **Result:** Failed with `Rate limit exceeded: HTTP 429: {'detail': 'Request was throttled. Rate limit exceeded: 1400/day. Expected available in 2185 seconds.'}`.

*(No web searches were executed. All lower-court orders in this case are unpublished state orders reproduced verbatim in the provisioned `record/documents/petition.txt` at Pet. App. 1a–8a.)*
