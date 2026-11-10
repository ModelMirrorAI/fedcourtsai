## Queries

### 1. Local Corpus Queries (`uv run fedcourts query`)
- `uv run fedcourts query --court scotus --docket-number 26-292`
  - Transfer stats: `ranged corpus reads: 18 GET(s), 4718592 byte(s)`
  - Purpose: Retrieve the corpus row for vide-linked companion petition No. `26-292` (*Fiona Havlish, et al. v. The Taliban, et al.*) to verify its distribution count, conference date, party/amicus appearances, and disposition status.
- `uv run fedcourts query --court scotus --docket-number 26-294`
  - Transfer stats: `ranged corpus reads: 0 GET(s), 0 byte(s)`
  - Purpose: Retrieve the corpus row for vide-linked companion petition No. `26-294` (*James Owens, et al. v. The Taliban, et al.*) to confirm synchronized relist status (`distribution_count: 2`, `distributed_for_conference: "2026-11-13"`).
- `uv run fedcourts query --court scotus --docket-number 24-699`
  - Transfer stats: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
  - Purpose: Retrieve the corpus row for *Exxon Mobil Corporation v. Corporación Cimex, S.A. (Cuba), et al.*, No. `24-699`, the intervening OT2025 decision on which Petition No. `26-293` bases its Question Presented 2 and GVR request.
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
  - Transfer stats: `ranged corpus reads: 37 GET(s), 9699328 byte(s)`
  - Purpose: Retrieve recent OT2026 granted petitions in the `2020s` era to inspect distribution counts and procedural profiles of relisted grants.
- `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
  - Transfer stats: `ranged corpus reads: 0 GET(s), 0 byte(s)`
  - Purpose: Retrieve recent OT2026 denied petitions from the November 9, 2026 order list to compare relisted denials.

### 2. CourtListener MCP Queries
- `mcp_courtlistener_search(type="o", citation="152 F.4th 339")` -> 0 results (reporter citation not yet indexed in search).
- `mcp_courtlistener_search(type="o", citation="170 F.4th 100")` -> 0 results (reporter citation not yet indexed in search).
- `mcp_courtlistener_search(type="o", court="ca2", case_name="Havlish v. The Taliban")` -> 0 results.
- `mcp_courtlistener_search(type="o", court="scotus", case_name="Exxon Mobil v. Corporacion CIMEX")` -> 0 results.
- `mcp_courtlistener_search(type="o", court=["scotus", "ca2"], q=""Da Afghanistan Bank"")` -> 2 results:
  - `cluster_id=10660852` / `opinion_id=11127439`: *Havlish v. Taliban; Aliganga v. Taliban*, Nos. 23-258(L), 23-354(L) (2d Cir. Aug. 26, 2025) (panel decision).
  - `cluster_id=10811059` / `opinion_id=11277807`: *Havlish v. Taliban; Aliganga v. Taliban*, Nos. 23-258(L), 23-354(L) (2d Cir. Mar. 19, 2026) (order and opinions denying rehearing en banc).
- `mcp_courtlistener_search(type="o", court="scotus", q=""CIMEX" "Helms-Burton"")` -> 1 result:
  - `cluster_id=10878536` / `opinion_id=11346053`: *Exxon Mobil Corp. v. Corporación Cimex, S.A. (Cuba)*, No. 24-699 (U.S. June 23, 2026).
- `mcp_courtlistener_read_document(opinion_id=11346053, chunk_index=[0, 1])`: Read the Syllabus and opening pages of Justice Kavanaugh's majority opinion in *Exxon Mobil Corp. v. Corporación Cimex, S.A. (Cuba)*, 609 U.S. ___ (June 23, 2026).
- `mcp_courtlistener_read_document(opinion_id=11277807, chunk_index=[0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10])`: Read the full text of the Second Circuit's March 19, 2026 en banc denial opinions (concurrence by Judge Nardini joined by Judge Lohier; dissent by Judge Sullivan joined by Chief Judge Livingston and Judges Bianco and Park; dissent by Judge Menashi; statement by Judges Cabranes and Calabresi), which had been truncated in Appendix B of `petition.txt`.

## Priors read

- **`scotus/72317507` (*Exxon Mobil Corporation v. Corporación Cimex, S.A. (Cuba), et al.*, No. `24-699`, decided June 23, 2026) & CourtListener `opinion_id=11346053`:** Selected because Petition No. `26-293` explicitly asks for a GVR or plenary review in light of *Cimex*. Reading the slip opinion showed that *Cimex* held that Title III of the Helms-Burton Act abrogates FSIA immunity without requiring plaintiffs to satisfy an FSIA exception. Because the Second Circuit panel below already held that TRIA § 201(a) abrogates FSIA immunity and provides independent jurisdiction (`petition.txt`, p. 51a), *Cimex* does not conflict with the Second Circuit's dispositive TRIA timing holding.
- **CourtListener `opinion_id=11277807` (*Havlish v. Taliban; Aliganga v. Taliban*, 170 F.4th 100 (2d Cir. Mar. 19, 2026) (en banc denial)):** Selected because Appendix B of `petition.txt` omitted 63,128 characters of the en banc opinions due to the 150,000-character pipeline cap (`petition.txt`, p. 74a). Reading the full text via CourtListener revealed the exact alignment and reasoning of the five dissenting active judges—specifically that Judge Menashi agreed with the panel that Executive recognition of Afghanistan as a "foreign state" is conclusive, while joining Judge Sullivan, Chief Judge Livingston, Judge Bianco, and Judge Park in concluding that DAB is no longer an "agency or instrumentality" of Afghanistan under 28 U.S.C. § 1603(b) and that TRIA § 201(a) instrumentality status must be assessed at the time of turnover rather than the time of blocking.
- **`scotus/9026000292` (*Fiona Havlish, et al. v. The Taliban, et al.*, No. `26-292`) and `scotus/9026000294` (*James Owens, et al. v. The Taliban, et al.*, No. `26-294`):** Selected as the two vide-linked companion petitions. Confirmed that all three petitions were relisted together for the November 13, 2026 Conference, that none of the three has a respondent appearance or a Call for a Response, and that `26-292` carries an amicus brief from Iowa and 30 other States.
- **`scotus/73520108` (*Goldman Sachs Bank USA v. Brown*, No. `25-1408`), `scotus/9026000012` (*Association for Education Fairness v. Montgomery County Board of Education*, No. `26-12`), `scotus/9026000204` (*Department of Justice v. McNutt*, No. `26-204`), `scotus/9026000018` (*Westcott v. Voice of the Experienced*, No. `26-18`), and `scotus/9026000107` (*Walls v. Prince George's County*, No. `26-107`):** Selected to compare recent OT2026 relisted grants and denials. Confirmed that relisted grants in private civil litigation consistently feature an appeared respondent and adversarial briefing prior to grant.

## Citation checks

- **Verified via Provisioned Appendix (`petition.txt`) and CourtListener MCP:**
  - *Havlish v. Taliban; Aliganga v. Taliban*, 152 F.4th 339 (2d Cir. Aug. 26, 2025), and 170 F.4th 100 (2d Cir. Mar. 19, 2026) (reh'g en banc denied): Verified full text and holdings in Appendix A (`petition.txt`, pp. 1a–71a) and CourtListener `opinion_id=11127439` and `opinion_id=11277807`.
  - *Exxon Mobil Corp. v. Corporación Cimex, S.A. (Cuba)*, No. 24-699, 609 U.S. ___ (June 23, 2026): Verified syllabus, holdings, and vote count (6–3, Kavanaugh, J.) via CourtListener `opinion_id=11346053` and corpus row `scotus/72317507`.
  - *Zivotofsky ex rel. Zivotofsky v. Kerry*, 576 U.S. 1 (2015), *Republic of Austria v. Altmann*, 541 U.S. 677 (2004), *Samantar v. Yousuf*, 560 U.S. 305 (2010), *Turkiye Halk Bankasi A.S. v. United States*, 598 U.S. 264 (2023), *Rubin v. Islamic Republic of Iran*, 583 U.S. 202 (2018), *Bank Markazi v. Peterson*, 578 U.S. 212 (2016), *Dole Food Co. v. Patrickson*, 538 U.S. 468 (2003), *Bartlett v. Baasiri*, 81 F.4th 28 (2d Cir. 2023), and *Kirschenbaum v. 650 Fifth Ave. & Related Props.*, 830 F.3d 107 (2d Cir. 2016): Verified as cited and analyzed across the petition and the Second Circuit majority and dissenting opinions (`petition.txt`, pp. 12–36, 24a–63a; CourtListener `opinion_id=11277807`).

## Gaps

- **Unprovisioned Amicus Briefs on the Cert Dockets:** The October 5, 2026 amicus curiae brief of Naseer A. Faiq (Chargé d'Affaires of the Permanent Mission of Afghanistan to the United Nations) filed in Nos. `26-292`, `26-293`, and `26-294`, and the October 8, 2026 amicus curiae brief of Iowa and 30 other States filed in No. `26-292`, are listed on the docket snapshots (`2026-11-09.json`; `26-292.json`) but their full text is not provisioned in `record/documents/` (which stages only the petition and questions presented per standard pipeline scope). However, Mr. Faiq's position in the Second Circuit is summarized in the panel and dissenting opinions (`petition.txt`, pp. 10a–11a, 57a).
- **Text of the Companion Petitions (`26-292` and `26-294`):** Only the docket snapshots (`record/related/26-292.json` and `record/related/26-294.json`) and corpus metadata rows are accessible under the single-cell isolation rule; the full petition texts of `26-292` and `26-294` are not staged in `9026000293/record/`, though their questions and procedural posture are extensively described in `petition.txt` and the consolidated Second Circuit opinions.
