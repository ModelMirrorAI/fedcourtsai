# Retrieval Log

## 1. Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number 26-117`
   - stderr: `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
   - Returned: `scotus/9026000117` (*Wes Allen, Alabama Secretary of State, et al. v. Evan Milligan, et al.*), docketed 2026-07-24, pending, `distributed_for_conference: 2026-11-13`, `distribution_count: 3`, `salience_score: 0.399`.

2. `uv run fedcourts query --court scotus --docket-number 26-118`
   - stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned: `scotus/9026000118` (*Wes Allen, Alabama Secretary of State, et al. v. Bobby Singleton, et al.*), docketed 2026-07-24, pending, `distributed_for_conference: 2026-11-13`, `distribution_count: 3`, `salience_score: 0.399`.

3. `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 5`
   - stderr: `ranged corpus reads: 33 GET(s), 8650752 byte(s)`
   - Returned: 5 recent GVR cases (`scotus/9026005123`, `scotus/73317900`, `scotus/73500268`, `scotus/73500579`, `scotus/9026000139`).

4. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   - stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned: 5 recent granted cases (`scotus/73520108`, `scotus/9526000512`, `scotus/9026000012`, `scotus/9026000204`, `scotus/9526000476`).

5. `uv run fedcourts query --court scotus --docket-number 25-243`
   - stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned: `scotus/73275185` (*Wes Allen, Alabama Secretary of State, et al. v. Marcus Caster, et al.*), docketed 2025-09-03, `date_cert_granted: 2026-05-11`, `disposition: granted`, `merits_decided: 2026-05-11`, `merits_judgment: vacated`.

6. `uv run fedcourts query --court scotus --docket-number 25-244`
   - stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned: `scotus/73275184` (*Demetric Simon v. Officer Keith Gladstone, et al.*), unrelated docket number check.

7. `uv run fedcourts query --court scotus --docket-number 25-245`
   - stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned: `scotus/73275186` (*Fire-Dex, LLC v. Admiral Insurance Company*), unrelated docket number check.

8. `uv run fedcourts query --court scotus --docket-number 25A1316`
   - stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned: `scotus/73500400` (*Wes Allen, Alabama Secretary of State, et al. v. Marcus Caster, et al.*), emergency stay application filed 2026-05-27, decided 2026-06-02 (`disposition: granted`, `interim_reading: granted`).

9. `uv run fedcourts query --court scotus --citation "146 S. Ct. 1377"`
   - stderr: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Returned: 0 rows (note on citation column coverage).

10. `uv run fedcourts query --court scotus --citation "146 S. Ct. 1131"`
    - stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
    - Returned: 0 rows (note on citation column coverage).

11. `uv run fedcourts query --court scotus --citation "146 S. Ct. 1196"`
    - stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
    - Returned: 0 rows (note on citation column coverage).

12. `uv run fedcourts query --court scotus --docket-number 24-109`
    - stderr: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
    - Returned: `scotus/69779623` (*Louisiana v. Phillip Callais, et al.*), `date_cert_granted: 2024-11-04`, `merits_decided: 2026-04-29`, `merits_judgment: affirmed`.

13. `uv run fedcourts query --court scotus --docket-number 25A1314`
    - stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
    - Returned: `scotus/73431862` (*Wes Allen, Alabama Secretary of State, et al. v. Evan Milligan, et al.*), stay application filed 2026-05-27, decided 2026-06-02 (`disposition: granted`).

14. `uv run fedcourts query --court scotus --docket-number 25A1315`
    - stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
    - Returned: `scotus/73500399` (*Wes Allen, Alabama Secretary of State, et al. v. Bobby Singleton, et al.*), stay application filed 2026-05-27, decided 2026-06-02 (`disposition: granted`).

15. `uv run fedcourts query --court scotus --era 2020s --disposition reversed --limit 5`
    - Failed with exit code 2 (`Unknown disposition 'reversed'; choose one of: granted, denied, granted-in-part, gvr, summary-reversal, dismissed, withdrawn, other`).

16. `uv run fedcourts query --court scotus --era 2020s --disposition summary-reversal --limit 10`
    - stderr: `ranged corpus reads: 1034 GET(s), 271056896 byte(s)`
    - Returned: 0 rows (summary reversals are stored under `granted` with same-day merits judgment).

17. `uv run fedcourts query --court scotus --era 2020s --disposition dismissed --limit 10`
    - stderr: `ranged corpus reads: 5 GET(s), 1310720 byte(s)`
    - Returned: 10 recent dismissed rows (`scotus/9026000002`, `scotus/9026000346`, `scotus/9026005347`, `scotus/73550516`, `scotus/9026005287`, `scotus/9026005309`, `scotus/73500379`, `scotus/73533825`, `scotus/73545844`, `scotus/9026005040`).

18. `uv run fedcourts query --court scotus --docket-number 25-241`
    - stderr: `ranged corpus reads: 15 GET(s), 3932160 byte(s)`
    - Returned: `scotus/73275181` (*Jason Arthur Aho v. Florida*), unrelated docket number check.

19. `uv run fedcourts query --court scotus --docket-number 25-242`
    - stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
    - Returned: `scotus/73275182` (*City of Houston, Texas v. The Commons of Lake Houston, Ltd.*), unrelated docket number check.

20. `uv run fedcourts query --court scotus --docket-number 25-243 --full`
    - stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
    - Returned: Full row for `scotus/73275185` (*Allen v. Caster*, No. 25-243).

21. `uv run fedcourts query --court scotus --docket-number 25-246`
    - stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
    - Returned: `scotus/73275187` (*Kenneth J. Jouppi v. Alaska*), unrelated docket number check.

22. `uv run fedcourts query --court scotus --docket-number 25-247`
    - stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
    - Returned: `scotus/73275188` (*Charles L. Payne, II v. Ohio*), unrelated docket number check.

23. `uv run fedcourts query --court scotus --docket-number 26-117 --full`
    - stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
    - Returned: Full row for `scotus/9026000117` (*Allen v. Milligan*, No. 26-117).

24. `uv run fedcourts query --court scotus --docket-number 26-118 --full`
    - stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
    - Returned: Full row for `scotus/9026000118` (*Allen v. Singleton*, No. 26-118).

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", citation="146 S. Ct. 1377")`
   - Returned: 0 results (S. Ct. pagination not yet indexed on CourtListener cluster).

2. `mcp_courtlistener_search(type="o", citation="146 S. Ct. 1131")`
   - Returned: 1 unrelated result (`202 Ct. Cl. 1131`).

3. `mcp_courtlistener_search(type="o", court="scotus", case_name="Abbott v. League of United Latin American Citizens", filed_after="2025-01-01")`
   - Returned: 0 results.

4. `mcp_courtlistener_search(type="o", court="scotus", case_name="Louisiana v. Callais")`
   - Returned: 2 results for *Louisiana v. Callais*, No. 24-109 (decided April 29, 2026; revision May 4, 2026, `cluster_id: 10852760`, `opinion_id: 11320154`).

5. `mcp_courtlistener_search(type="o", court="scotus", case_name="Allen v. Milligan", filed_after="2026-01-01")`
   - Returned: 1 result for *Allen v. Milligan*, Nos. 25A1314, 25A1315, 25A1316 (decided June 2, 2026, `cluster_id: 10869022`, `opinion_id: 11336479`).

6. `mcp_courtlistener_search(type="o", docket_number="25A624")`
   - Returned: 0 results.

7. `mcp_courtlistener_read_document(opinion_id=11336479)`
   - Returned: Full text (52,827 chars) of the June 2, 2026 *per curiam* stay order and Justice Sotomayor's dissent in *Allen v. Milligan*, Nos. 25A1314, 25A1315, and 25A1316 (which stayed the May 26, 2026 preliminary injunctions at issue in this petition and companion appeals).

8. `mcp_courtlistener_read_document(opinion_id=11320154, chunk_index=[0, 1, 2], chunk_size=8000)`
   - Returned: Chunks 0–2 of *Louisiana v. Callais*, No. 24-109 (syllabus and opening of majority opinion).

9. `mcp_courtlistener_search(type="o", court="scotus", case_name="Allen v. Caster", filed_after="2026-01-01")`
   - Returned: 0 results.

10. `mcp_courtlistener_search(type="o", court="scotus", docket_number="25-243")`
    - Returned: 0 results.
