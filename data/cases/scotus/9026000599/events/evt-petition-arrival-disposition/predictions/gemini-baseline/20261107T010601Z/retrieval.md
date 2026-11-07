# Retrieval Log: `scotus/9026000599` (`evt-petition-arrival-disposition`)

## 1. Provisioned Case Files Read (`data/cases/scotus/9026000599/`)

- `events/evt-petition-arrival-disposition/event.yaml` — event definition (`stage: cert`, `moment: arrival`, `opened_at: 2026-11-06`).
- `record/context.json` — frozen conditioning context (`mode: forward`, `band: baseline`, `salience_version: sal-v7`, `term: 2026`, `cert_anchor.rate: 0.051512996760685784`, `distribution_count: 0`, `cvsg_date: null`, `amicus_briefs: 0`).
- `record/same-question.json` — sibling/companion petition index (`petitions: []`).
- `record/snapshots/2026-11-07.json` — truncated arrival-date SCOTUS docket snapshot (`CaseNumber: "26-599 "`, `DocketedDate: "November 6, 2026"`, `LowerCourt: "United States Court of Appeals for the District of Columbia Circuit"`).
- `record/documents/documents.json` — document manifest.
- `record/documents/questions-presented.txt` — single Question Presented ("Whether the district court erred in enjoining the ongoing renovation of the East Wing at the White House.").
- `record/documents/lower-court-docket.txt` — D.C. Circuit docket summary (`cadc`, `No. 26-5123`, judgment date `2026-08-07`, no rehearing en banc petition filed).
- `record/documents/petition.txt` — Solicitor General's Petition for a Writ of Certiorari (`No. 26-599`) and Appendices, including Appendix A (the Supreme Court's August 31, 2026 per curiam stay opinion and Chief Justice Roberts's 4-Justice dissent in `No. 26A203`, `1a`–`16a`) and Appendix B (the D.C. Circuit's August 7, 2026 opinion, `17a`–`159a`).
- `record/documents/decision-below.txt` — D.C. Circuit slip opinion (`No. 26-5123`, consolidated with `No. 26-5134`, decided August 7, 2026).
- `metrics/statpack.md` — pooled historical base rates (`baseline` and `federal` salience band `[reached]` rates across OT2017–OT2025, relist rates, and conditional grant rates).

## 2. Corpus Queries (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number 26A203`
   - Transfer: `ranged corpus reads: 15 GET(s), 3932160 byte(s)`
   - Returned `scotus/9526000203` (*National Park Service, et al. v. National Trust for Historic Preservation in the United States*, `No. 26A203`, filed `2026-08-14`, decided `2026-08-31`, `disposition: "granted"`, `amicus_briefs: 7`, `referred_to_court: true`).
2. `uv run fedcourts query --court scotus --docket-number 25-845`
   - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned `scotus/73280347` (*Greg Abbott, in His Official Capacity as Governor of Texas, et al. v. League of United Latin American Citizens, et al.*, `No. 25-845`, cited at Pet. 10, 12).
3. `uv run fedcourts query --court scotus --docket-number 26A308`
   - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Returned `scotus/9526000308` (*Department of Homeland Security, et al. v. League of Women Voters, et al.*, `No. 26A308`, decided `2026-09-25`, `disposition: "granted"`).
4. `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 5`
   - Transfer: `ranged corpus reads: 29 GET(s), 7602176 byte(s)`
   - Returned 5 resolved `gvr` priors (`scotus/73317900` `25-1269`, `scotus/73500268` `25-1367`, `scotus/73500579` `25-7569`, `scotus/9026000139` `26-139`, `scotus/9026005216` `26-5216`), showing typical `distribution_count: 2` (1 relist) before GVR orders.
5. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned 5 resolved `granted` priors (`scotus/9526000512` `26A512`, `scotus/9026000012` `26-12`, `scotus/9026000204` `26-204`, `scotus/9526000476` `26A476`, `scotus/73281386` `25-1103`), showing Solicitor General cert grants (`26-204`, `25-1103`) relisting once (`distribution_count: 2`) before grant.

## 3. CourtListener MCP Calls

1. `mcp_courtlistener_search(type="o", court="cadc", case_name="National Trust for Historic Preservation v. National Park Service", num_results=5, fields=["caseName", "docketNumber", "dateFiled", "cluster_id", "opinions"])`
   - Returned 1 result: `cluster_id: 10844746` (`National Trust for Historic Preservation in the United States v. National Park Service`, `No. 26-5123`, `dateFiled: 2026-04-17`, administrative stay order).

## 4. Web Searches

None required (the provisioned `petition.txt` and `decision-below.txt` contained the complete certiorari petition, the Supreme Court's August 31, 2026 stay opinion and dissent in `No. 26A203`, and the D.C. Circuit's August 7, 2026 majority opinion).
