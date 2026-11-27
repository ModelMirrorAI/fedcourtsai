# Retrieval Log

All lookups beyond the provisioned case inputs (`data/cases/scotus/9026000549/record/`, `event.yaml`, and `metrics/statpack.md`) are recorded below. No outcome or third-party forecast of this case was sought or encountered.

## 1. Local / Ranged Corpus Queries (`fedcourts`)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - **Transfer stderr:** `ranged corpus reads: 41 GET(s), 10747904 byte(s)`
   - **Returned:** 10 granted 2020s SCOTUS rows (e.g., `scotus/73280982` *Robinhood Markets, Inc. v. Sodha*, No. 25-944, `distribution_count: 3`, `cvsg_date: 2026-06-01`).
   - **Impact:** Confirmed typical multi-distribution / CVSG / amicus profile of granted paid OT2025/OT2026 petitions relative to once-distributed SG-waived petitions.

2. `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 10` (re-run at `--limit 5` to confirm exact stderr line after collapsed combined output)
   - **Transfer stderr:** `ranged corpus reads: 0 GET(s), 0 byte(s)` (warm local/service cache on second pass)
   - **Returned:** Recent 2020s denied SCOTUS rows (e.g., `scotus/9526000729`, `scotus/9026006154`).
   - **Impact:** Confirmed baseline structure of denied SCOTUS rows in the 2020s corpus slice.

3. `uv run fedcourts query --court scotus --attorney "Lori Alvino McGill" --limit 20` *(failed flag check)*
   - **Transfer stderr:** None (CLI usage error: `No such option: --attorney`).
   - **Impact:** Confirmed `fedcourts query` filters (`--court`, `--docket-number`, `--topic`, `--judge`, `--citation`, `--disposition`, `--era`, etc.) do not filter by attorney name.

4. `uv run fedcourts query --court scotus --docket-number 24-362 --limit 5`
   - **Transfer stderr:** `ranged corpus reads: 17 GET(s), 4456448 byte(s)`
   - **Returned:** `scotus/69979990` (*Curtrina Martin, et al. v. United States, et al.*, No. 24-362, granted and decided June 12, 2025, with extensive amicus participation).
   - **Impact:** Contrasted *Martin*'s heavy public-interest and amicus mobilization at the cert/merits stages against this petition's `cert_amicus_briefs = 0` and SG waiver.

5. `uv run fedcourts open-events --court scotus` *(failed missing-docket check)* and `uv run fedcourts open-events --court scotus --docket 9026000549`
   - **Transfer stderr:** None (`open-events` emits no transfer line).
   - **Returned:** `evt-petition-disposition` on `scotus/9026000549`.
   - **Impact:** Confirmed `evt-petition-disposition` is the sole open event on this docket.

6. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 40` (run once piped to `grep` and once piped to `head -n 2` to capture the header transfer line)
   - **Transfer stderr:** `ranged corpus reads: 28 GET(s), 7340032 byte(s)`
   - **Returned:** 40 recent granted 2020s SCOTUS dockets (including OT2025/OT2026 grants involving the United States).
   - **Impact:** Verified that no pending OT2025/OT2026 SCOTUS merits grant presents the 28 U.S.C. § 2680(c) / § 2680(h) question, directly lowering `gvr` and `summary-disposition-route` (`0.12`).

## 2. CourtListener MCP Lookups

1. `search(type="o", q='"2680(c)" AND "2680(h)" AND ("Gasho" OR "Jeanmarie")', num_results=15)`
   - **Returned:** 14 opinions, led by *Angulo v. Brown*, 978 F.3d 942 (5th Cir. 2020) (`cluster_id: 4799824`), *Jeanmarie v. United States*, 242 F.3d 600 (5th Cir. 2001) (`cluster_id: 772359`), *Davinci Aircraft, Inc. v. United States*, 926 F.3d 1117 (9th Cir. 2019) (`cluster_id: 4628722`), *Snyder & Assocs. Acquisitions LLC v. United States*, 859 F.3d 1152 (9th Cir. 2017) (`cluster_id: 4401098`), and *Gasho v. United States*, 39 F.3d 1420 (9th Cir. 1994) (`cluster_id: 682438` / `7030706`).
   - **Impact:** Confirmed that no third federal court of appeals has squarely joined either side of the CA5/CA9 split on simultaneous checkpoint vehicle-detention personal-injury torts over the past three decades, restraining `P(grant)`.

2. `search(type="o", q='"Angulo v. Brown" OR ("Jeanmarie" AND "2680(c)" AND certiorari)', num_results=10)`
   - **Returned:** 6 circuit opinions citing *Angulo* or *Jeanmarie* (*Parrott v. United States*, 536 F.3d 629 (7th Cir. 2008); *Elhady v. Unidentified CBP Agents*, 18 F.4th 880 (6th Cir. 2021); Fifth Circuit qualified-immunity citations).
   - **Impact:** Confirmed *Parrott* involved prisoner property detention post-*Ali* rather than personal-injury checkpoint torts.

3. `search(type="o", court="scotus", q='"Martin v. United States" "2680(h)"', num_results=10)`
   - **Returned:** *Martin v. United States*, 605 U.S. 395, 145 S. Ct. 1689 (2025) (`cluster_id: 10603452`, No. 24-362).
   - **Impact:** Located the exact SCOTUS precedent applied by the Fifth Circuit below.

4. `get_endpoint_item(endpoint_id="clusters", item_id=10603452 | 4799824 | 682438 | 4628722)` (4 cluster metadata calls)
   - **Returned:** Sub-opinion IDs `11070040` (*Martin*, authored by Justice Gorsuch), `4580171` (*Angulo*), `682438` (*Gasho*), and `4405975` (*Davinci Aircraft*).
   - **Impact:** Identified exact opinion IDs for targeted text verification.

5. `read_document(opinion_id=11070040, chunk_index=[0, 3, 4])` and `read_document(opinion_id=11070040, chunk_index=[6, 7, 8, 9])`
   - **Returned:** Syllabus, Justice Gorsuch's unanimous opinion for the Court, and Justice Sotomayor's concurring opinion (joined by Justice Jackson) in *Martin v. United States*, 605 U.S. 395 (2025).
   - **Impact:** Informed both our upward adjustment over `cert_amicus_line` (statutory adjacency to *Martin* and potential CFR interest) and our `order-writers` / `dissent-from-denial` weights (`Sotomayor: 0.014`, `Gorsuch: 0.009`, `Jackson: 0.005`).

6. `search_document(opinion_id=[4580171, 682438, 4405975], query="2680(c)", snippet_size=450)`
   - **Returned:** Relevant passages in *Angulo*, *Gasho*, and *Davinci Aircraft*.
   - **Impact:** Revealed that *Gasho* (39 F.3d at 1434) rested on a one-sentence Government concession regarding subsequent arrests while affirming summary judgment for the United States on other grounds — substantially weakening the perceived urgency of the alleged circuit conflict.

7. `search(type="o", court="scotus", q='"Angulo" AND "Brown"', num_results=10)`
   - **Returned:** 3 unrelated SCOTUS opinions (*Grimmett v. Brown*, *Fogerty v. Fantasy*, *Almonester v. Kenton*); no SCOTUS opinion in *Angulo v. Brown*.
   - **Impact:** Confirmed no prior SCOTUS merits or written cert-denial opinion in *Angulo*.
