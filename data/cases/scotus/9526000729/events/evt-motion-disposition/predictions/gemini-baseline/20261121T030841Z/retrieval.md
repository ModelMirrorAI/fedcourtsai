# Retrieval Log — `scotus/9526000729` (`evt-motion-disposition`)

Mode: `forward` (`cutoff: 2026-11-18`, `cut_kind: arrival-position`). Per the prompt rules, no lookup targeted `26A729`'s own live disposition or any external forecast.

## 1. CLI Path Resolution and Corpus Queries (`fedcourts`)

1. `uv run fedcourts paths --court "scotus" --docket "9526000729" --event "evt-motion-disposition" --role predictor`
   - Result: resolved `case_id = scotus/9526000729`, `corpus = corpus/corpus.db`, and `event.yaml` path; confirmed `DECIDED_BEFORE` unset (`forward` mode).
2. `uv run fedcourts query --court scotus --era 2020s --limit 15`
   - Stderr: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Result: returned 15 recent resolved 2020s SCOTUS priors, including recent OT2026 substantive interim applications `26A686` (*Overton v. Florida*, capital, referred, denied), `26A714` (*Mullin v. National TPS Alliance*, withdrawn), `26A715` (*Rachel Beth Odom v. Oklahoma*, non-capital state civil appeals, `referred_to_court: false`, `response_requested: false`, `amicus_briefs: 0`, denied), `26A716` (*Dennes v. Texas*, capital, referred, denied), and `26A698` (*Simpkins v. Tennessee*, *pro se*, `referred_to_court: false`, `response_requested: false`, denied).
3. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Stderr: `ranged corpus reads: 30 GET(s), 7864320 byte(s)`
   - Result: returned 10 recent granted 2020s SCOTUS priors, including granted substantive interim applications `26A560` (*Mullin v. Friends of the Ruidosa Church*), `26A512` (*Scanlan v. Coalition for Open Democracy*), and `26A476` (*FCC v. Brown*) — all federal/state institutional applicants with `referred_to_court: true` and responses on file.
4. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 40`
   - Stderr: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: returned 40 recent denied 2020s SCOTUS priors (confirming the same recent denied application cohort alongside denied cert petitions).

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", q='"Buenaventura" "Buot"', fields=[...])`
   - Result: 0 opinions (`query_id="d2997c94"`).
2. `mcp_courtlistener_search(type="o", court="me", q='"Buenaventura" OR "And-26-291"', fields=[...])`
   - Result: 0 published Maine Supreme Judicial Court opinions (`query_id="c89e1465"`).
3. `mcp_courtlistener_search(type="r", party_name="Buenaventura", fields=[...])`
   - Result: 839 RECAP dockets (`query_id="3736815a"`), surfacing recent *pro se* E.D. Texas dockets `Buenaventura v. Plano Police Department`, No. `4:26-cv-01666` (`docket_id=75091272`, filed 2026-11-09), and `Buenaventura v. FMR, LLC`, No. `4:26-cv-01019` (`docket_id=75000432`).
4. `mcp_courtlistener_search(type="r", party_name='"Ian Buenaventura"', fields=[...])`
   - Result: 0 exact-phrase RECAP matches (`query_id="6e8a772d"`, because dockets include middle initials `Ian R.` / `Ian S.R.`).
5. `mcp_courtlistener_search(type="r", party_name='"Buot"', fields=[...])`
   - Result: 18 unrelated RECAP dockets (`query_id="d972fc51"`).
6. `mcp_courtlistener_search(type="r", court="med", party_name="Buenaventura", fields=[...])`
   - Result: 5 District of Maine dockets (`query_id="48f664c1"`), including `IN RE: BUENAVENTURA`, No. `2:25-mc-00465` (`docket_id=71699259`, filed 2025-10-16), and `BUENAVENTURA v. EXECUTIVE OFFICE OF THE PRESIDENT`, No. `2:24-cv-00089` (`docket_id=68366349`, filed 2024-03-21).
7. `mcp_courtlistener_get_endpoint_item(endpoint_id="dockets", item_id=75091272, fields=[...])`
   - Result: metadata for `Buenaventura v. Plano Police Department`, No. `4:26-cv-01666` (E.D. Tex. filed 2026-11-09).
8. `mcp_courtlistener_call_endpoint(endpoint_id="parties", query={"docket": 71699259, "fields": ["id", "name"]})`
   - Result: party listed as `"ENJOINED FILER IAN R BUENAVENTURA"`.
9. `mcp_courtlistener_call_endpoint(endpoint_id="docket-entries", query={"docket": 71699259, "fields": [...]})`
   - Result: 2 entries — Oct. 16, 2025 motion for leave to file a notice of removal and motion to file under seal; Oct. 20, 2025 Order by Judge Lance E. Walker denying leave to file because the proposed removal of state divorce and child-custody proceedings fell outside federal jurisdiction under *Ankenbrandt v. Richards*, 504 U.S. 689, 703 (1992).
10. `mcp_courtlistener_call_endpoint(endpoint_id="docket-entries", query={"docket": 75091272, "fields": [...]})`
    - Result: Nov. 9, 2026 *pro se* complaint and IFP motion in E.D. Texas (`4:26-cv-01666`).
11. `mcp_courtlistener_call_endpoint(endpoint_id="docket-entries", query={"docket": 68366349, "fields": [...]})`
    - Result: docket entries in `Buenaventura v. Executive Office of the President` (`2:24-cv-00089`, D. Me., dismissed May–June 2024).
12. `mcp_courtlistener_search(type="r", court=["ca1", "ca5"], party_name="Buenaventura", fields=[...])`
    - Result: 0 First or Fifth Circuit RECAP dockets (`query_id="822e6cb5"`).
13. `mcp_courtlistener_search(type="o", court=["med", "ca1", "txed"], q="Buenaventura", fields=[...])`
    - Result: 0 indexed opinions (`query_id="45d1432c"`).
14. `mcp_courtlistener_search(type="rd", court=["med", "txed"], party_name="Buenaventura", available_only=true, fields=[...])`
    - Result: 0 available RECAP document PDFs (`query_id="e0f1a1d5"`).
15. `mcp_courtlistener_search(type="o", court="me", filed_after="2026-09-01", q='"And-26-291" OR "Buot"', fields=[...])`
    - Result: 0 Maine Supreme Judicial Court opinions (`query_id="7f7bae27"`).

## 3. Web Search and Public Docket Fetches

1. `google_web_search(query='"And-26-291" OR ("Buenaventura" "Leslie Buot") -26A729 -fedcourts -scotus')`
   - Result: surfaced pre-decision background on the Maine divorce litigation (`Buot v. Buenaventura`, Androscoggin County District Court and Maine Supreme Judicial Court `And-25-246`, dismissed June 24, 2025 as interlocutory over an anti-SLAPP motion and challenge to Maine's irreconcilable-differences divorce standard), prior SCOTUS stay application `25A572`, and related IFP certiorari petition `26-5639`. No mention of `26A729` or any forecast surfaced.
2. `web_fetch` on `https://www.supremecourt.gov/docket/docketfiles/html/public/25a572.html`
   - Result: official docket for *Ian Buenaventura v. Leslie Buot*, No. `25A572` (from `And-25-246`): submitted to Justice Jackson Nov. 7, 2025; denied by Justice Jackson Nov. 17, 2025 (no response requested, no referral); refiled to Justice Alito Apr. 8, 2026, referred to the Court Apr. 22, 2026, and denied by the Court May 18, 2026.
3. `web_fetch` on `https://www.supremecourt.gov/docket/docketfiles/html/public/26-5639.html`
   - Result: official docket for *Ian S. R. Buenaventura v. Leslie G. C. Buot*, No. `26-5639` (from `And-25-246`): extensions `25A377` and `25A1097` granted by Justice Jackson; IFP cert petition docketed Sept. 22, 2026; distributed Nov. 5, 2026 for the Conference of Dec. 4, 2026.
4. `google_web_search(query='"motion for leave to file application" "under seal" site:supremecourt.gov -26A729 -Buenaventura')`
   - Result: confirmed Supreme Court Rule 34.7 paper-only filing rules for motions to file under seal and surfaced recent chambers-resolved analogues `26A715` (*Rachel Beth Odom v. Oklahoma*, Nov. 19, 2026 — motion to file under seal granted and stay denied by Justice Gorsuch alone) and `26A325` (*M.W. v. Superior Court of California*, Sept. 22, 2026).
