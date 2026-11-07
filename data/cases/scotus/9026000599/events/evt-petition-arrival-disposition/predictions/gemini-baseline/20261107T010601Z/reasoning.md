# Prediction Reasoning: `scotus/9026000599` (`evt-petition-arrival-disposition`)

## 1. Case Overview & Procedural Posture at Arrival

- **Case:** *National Park Service, et al. v. National Trust for Historic Preservation in the United States*, No. 26-599 (docketed November 6, 2026; `moment: arrival`, `input_snapshot: 2026-11-07.json`).
- **Petitioners:** The National Park Service (NPS), Department of the Interior, General Services Administration, Executive Office of the President (EOP), Office of the Executive Residence (EXR), President Donald J. Trump, and associated federal officials, represented by Solicitor General D. John Sauer.
- **Respondent:** The National Trust for Historic Preservation in the United States, a congressionally chartered nonprofit organization (54 U.S.C. § 312102(a)) headquartered on Lafayette Square across from the White House.
- **Question Presented:** "Whether the district court erred in enjoining the ongoing renovation of the East Wing at the White House."
- **Background and Lower-Court Rulings:**
  - In October 2025, at President Trump's direction, the East Wing of the White House was demolished as part of a roughly $400 million privately funded project to construct a 90,000-square-foot state ballroom on the former East Wing site in President's Park alongside underground military and security infrastructure.
  - The National Trust sued in the U.S. District Court for the District of Columbia (`No. 1:25-cv-04316`, Judge Richard J. Leon). After denying a TRO (`National Trust I`, 813 F. Supp. 3d 42) and an initial preliminary injunction motion before ultra vires claims were added (`National Trust II`, 821 F. Supp. 3d 62), the district court on March 31, 2026 (`National Trust III`, 827 F. Supp. 3d 93) and by amended order on April 16, 2026 (`National Trust IV`, 2026 WL 1027744) preliminarily enjoined above-ground construction of the ballroom while exempting below-ground construction and strictly necessary safety/security measures that do not lock in the above-ground size and scale of the ballroom.
  - On August 7, 2026, a divided panel of the D.C. Circuit (Judges Millett and Garcia; Judge Rao dissenting) affirmed the modified preliminary injunction (`No. 26-5123`, consolidated with `No. 26-5134`, App. 17a–159a). The panel majority held that (1) the Trust established associational standing through its member and trustee Professor Alison K. Hoagland, an architectural historian and Capitol Hill resident who regularly visits President's Park and Lafayette Square to view the White House; (2) the ballroom construction likely violated 40 U.S.C. § 8106 (prohibiting erection of any building or structure on federal park grounds in the District of Columbia "without express authority of Congress") and was not authorized by 3 U.S.C. § 105(d)(1), the NPS Organic Act (54 U.S.C. § 100101(a)), or the Economy Act (31 U.S.C. § 1535); and (3) the balance of equities favored preliminary relief. Judge Rao dissented on standing, statutory authority, and the equities.
- **The Supreme Court's August 31, 2026 Stay Decision (`No. 26A203`):**
  - On August 31, 2026, the Supreme Court granted the Solicitor General's application (`No. 26A203`) to stay the district court's injunction pending the filing and disposition of a petition for a writ of certiorari (App. 1a–16a).
  - Crucially, the Court issued a 9-page **per curiam opinion** (App. 1a–9a) joined by five Justices (Justices Thomas, Alito, Gorsuch, Kavanaugh, and Barrett), over a 7-page dissent by Chief Justice Roberts joined by Justices Sotomayor, Kagan, and Jackson (App. 10a–16a).
  - In Part I of the per curiam opinion (App. 3a–6a), the Court held that "the government is likely to succeed on the merits because the Trust likely lacks Article III standing to bring this suit," concluding that Professor Hoagland's asserted injury from viewing a ballroom whose scale, height, and massing she dislikes amounts to "mere offense, disagreement, or distaste" rather than a concrete and particularized injury under *FDA v. Alliance for Hippocratic Medicine*, 602 U.S. 367, 390 n.3 (2024), *Valley Forge Christian College v. Americans United for Separation of Church and State, Inc.*, 454 U.S. 464, 485 (1982), and *Lujan v. Defenders of Wildlife*, 504 U.S. 555, 560–563 (1992).
  - In Part II (App. 6a–9a), the Court held that the government also established irreparable harm and favorable equities under *Trump v. CASA, Inc.*, 606 U.S. 831, 859 (2025), and *Winter v. NRDC*, 555 U.S. 7, 25–26 (2008), crediting declarations from the Secretaries of State, Homeland Security, and the Army and the Directors of National Intelligence, the CIA, the FBI, and the Secret Service that the height and mass of the above-ground structure are crucial to shield the below-ground military facility from kinetic impacts and that construction delays impair protective operations.

## 2. Base-Rate Anchoring (`context.json` and `metrics/statpack.md`)

At `moment: arrival`, no conference distribution, relist, or CVSG has yet occurred (`distribution_count: 0`, `cvsg_date: null`, `amicus_briefs: 0`).

1. **Frozen `context.json` Salience Band (`baseline`):**
   - `record/context.json` froze `"band": "baseline"` under `"salience_version": "sal-v7"` for `"term": 2026`, with `"cert_anchor": {"rate": 0.051512996760685784, "lookback_terms": 10, "statpack_digest": "sha256:12982c9a25e7998d76e1aafb22b3a4e1058f56190eb0966126deae0fd1c3c54d"}`.
   - In `metrics/statpack.md` (*Segment base rate by salience band (`sal-v7`)*), the `baseline` `[reached]` rates across all Terms strictly preceding OT2026 (OT2017–OT2025) are:
     - OT2025: 5.0% (`n=1289`)
     - OT2024: 4.5% (`n=1243`)
     - OT2023: 5.5% (`n=1283`)
     - OT2022: 5.2% (`n=1183`)
     - OT2021: 6.1% (`n=1469`)
     - OT2020: 5.8% (`n=1697`)
     - OT2019: 5.0% (`n=1369`)
     - OT2018: 5.0% (`n=1509`)
     - OT2017: 4.3% (`n=1615`)
   - Pooled across OT2017–OT2025 (`n=12,657`), the `baseline` `[reached]` grant rate is **5.15%** (`0.051513`), which is the exact `cert_anchor.rate` against which this cell's Brier skill is scored.
2. **True Substantive Arrival Class (`federal` Petitioner):**
   - Why did `sal-v7` assign `"band": "baseline"` at arrival? Because the docket caption is `"National Park Service, et al., Petitioners"`, which lacks `"United States"` or a cabinet officer title matched by `sal-v7`'s caption heuristic (documented in `flags.json`).
   - Substantively, however, this is a Solicitor General petition filed on behalf of federal agencies and the President of the United States. In `metrics/statpack.md` (*Segment base rate by salience band (`sal-v7`)*), the `federal` band's `[reached]` rate—the arrival-time base rate for federal petitioners across all Terms strictly preceding OT2026 (OT2017–OT2025)—is:
     - OT2025: 57.1% (`n=28`, ~16 grants)
     - OT2024: 62.5% (`n=16`, 10 grants)
     - OT2023: 86.7% (`n=30`, 26 grants)
     - OT2022: 89.5% (`n=19`, 17 grants)
     - OT2021: 75.0% (`n=12`, 9 grants)
     - OT2020: 67.4% (`n=43`, 29 grants)
     - OT2019: 96.3% (`n=27`, 26 grants)
     - OT2018: 47.6% (`n=21`, 10 grants)
     - OT2017: 75.0% (`n=16`, 12 grants)
   - Pooled across OT2017–OT2025, the `federal` arrival base rate is **155 / 212 = 73.1%** (`0.7311`).

## 3. Case-Specific Updating from the Anchor to `P(grant) = 0.88` and `predicted_disposition = "gvr"`

Starting from the frozen `baseline` anchor of **5.15%** and the empirical `federal` Solicitor General arrival rate of **73.1%**, case-specific structural features push the binary grant probability (`granted: 1`, covering plenary grants, GVRs, and summary reversals) upward to **0.88** (`88%`), with **`gvr`** (`60%`) as the modal disposition label over plenary **`granted`** (`26%`) and **`summary-reversal`** (`2%`):

1. **Automatic Termination of the August 31, 2026 Stay Upon Denial of Certiorari:**
   - The decretal paragraph of the Court's August 31, 2026 stay order in `No. 26A203` explicitly states (App. 9a):
     > *"The injunction entered by the United States District Court for the District of Columbia in case No. 1:25-cv-04316 is stayed pending the filing and disposition of the government's petition for a writ of certiorari, if such writ is timely sought. Should certiorari be denied, this stay shall terminate automatically. In the event certiorari is granted, the stay shall terminate upon the sending down of the judgment of this Court."*
   - Because the D.C. Circuit had already entered its judgment affirming the preliminary injunction on August 7, 2026—before the Supreme Court's August 31, 2026 stay—the preliminary injunction remains on the books below. As Justice Barrett explained in *National Institutes of Health v. American Public Health Ass'n*, 145 S. Ct. 2658, 2661 (2025) (cited at Pet. 10), denying certiorari when an erroneous preliminary injunction remains on the books below causes the stay to expire and the enjoined order to spring back into effect.
   - Five Justices (Thomas, Alito, Gorsuch, Kavanaugh, and Barrett) have already joined a published per curiam opinion in this exact case holding both that the National Trust likely lacks Article III standing and that the injunction inflicts irreparable national-security harm on the Executive Branch. Those five Justices will not vote to simply deny certiorari and allow the stayed injunction to automatically reactivate.

2. **Why `gvr` (60%) Leads Plenary `granted` (26%) Within the 88% Grant-Side Probability (`summary-disposition-route: 0.70`):**
   - Notice the Solicitor General's explicit primary relief request in the Petition (Pet. 10, 12–13, 30):
     > *"Because the Court has already concluded that the requirements for a preliminary injunction are not met here, for reasons explained at length in the Court's stay opinion, see id. at 2a-9a, there is no need for additional briefing and oral argument regarding the validity of the preliminary injunction. Instead, the Court should simply vacate the court of appeals' decision and remand for further proceedings consistent with the stay opinion—as the Court has recently done in a similar posture. See Abbott v. League of United Latin American Citizens, No. 25-845 (Oct. 13, 2026)... The petition for a writ of certiorari should be granted and the judgment of the court of appeals should be vacated. In the alternative, the petition should be granted and the case should be set for briefing and oral argument."*
   - Under `schemas/prediction.schema.json`, any order that grants the petition, vacates the judgment below, and remands—whether a merits vacatur-and-remand in light of the Court's stay opinion (`gvr` + `standard`) or a mootness vacatur under *United States v. Munsingwear, Inc.*, 340 U.S. 36 (1950) (`gvr` + `mootness`)—resolves to the disposition label **`gvr`** and counts as `granted: 1` on the binary axis.
   - A vacatur and remand (`gvr`, **60%**) is the path of least resistance for the five-Justice per curiam majority:
     - They have already written a full 9-page opinion explaining why the preliminary injunction fails on Article III standing and *Winter* equities (`No. 26A203`, App. 1a–9a).
     - Vacating and remanding for further proceedings consistent with the stay opinion disposes of the preliminary injunction without requiring full merits briefing and oral argument on an interlocutory record or forcing the Court to definitively adjudicate the statutory merits under 40 U.S.C. § 8106, 3 U.S.C. § 105(d)(1), and 54 U.S.C. § 100101(a) (issues the stay majority deliberately avoided reaching in `No. 26A203`, App. 9a).
     - In addition, because construction of the ballroom has proceeded under the stay since August 31, 2026, if above-ground construction reaches a stage that moots the preliminary-injunction appeal before conference disposition, the Court would likewise grant, vacate, and remand under *Munsingwear* (`gvr`).
   - Plenary review (**`granted`, 26%**) remains the second most likely outcome: four Justices (Chief Justice Roberts and Justices Sotomayor, Kagan, and Jackson) dissented in `No. 26A203` and it takes only four votes to grant plenary review, or one or more members of the stay majority might prefer full briefing before issuing a merits judgment on Article III aesthetic standing in historic-preservation suits. However, the four stay dissenters have a strong strategic disincentive to force plenary merits review of this interlocutory appeal given the 5-Justice per curiam opinion already locked in against standing on the current preliminary-injunction record.
   - Outright summary reversal without remand phrasing (**`summary-reversal`, 2%**) is unlikely given the SG's explicit request to vacate the D.C. Circuit's judgment and remand.
   - Conditional on a grant (`0.88`), the probability that the Court disposes of the case in the cert order itself (`gvr` `0.60` + `summary-reversal` `0.02` = `0.62`) rather than setting the case for plenary briefing and argument (`0.26`) is `0.62 / 0.88 = 0.7045`, so we set **`summary-disposition-route: 0.70`**.
   - Non-grant outcomes (**`denied`, 9%; `dismissed`/`withdrawn`, 3%**) would occur almost exclusively if the district court dissolves the preliminary injunction or the parties stipulate to dismissal of the preliminary-injunction claims before the Court acts on the petition, eliminating the need for Supreme Court action.

## 4. Secondary Claims and Distributions (`cert-v3`)

- **`relist-increment: 0.78`:**
  - At `moment: arrival`, the snapshot shows `0` conference distributions (`distribution_count: 0`). In `metrics/statpack.md`, the overall relist rate across the docket in OT2025 is 10.7%, and in the paid scored segment (*Cert petitions by relist count*), `0` relists has `n=1840` (grant rate 0.7%, GVR 0.8%) while `1` relist (`n=505`, grant 28.5%, GVR 10.5%) and `2` relists (`n=100`, grant 27.0%, GVR 9.0%) carry the bulk of grants and GVRs. Because the Court's settled practice is to distribute a petition at least twice (one relist after initial conference distribution) before issuing a grant, GVR, or summary vacatur, we estimate a **0.78** probability of at least one distribution beyond the first conference (which, from arrival's `0` distributions, means `distribution_count >= 1` and specifically relisting before disposition).
- **`cvsg-increment: 0.001`:**
  - The Solicitor General is counsel of record for Petitioners. The Court does not invite the Solicitor General to file an amicus brief when federal agencies represented by the SG are already petitioners.
- **`dissent-from-denial: 0.25`:**
  - Conditional on the unlikely event of a denial, the main pathway to a denial is that the preliminary injunction was already dissolved or mooted in the district court, in which case a noted dissent or statement is unlikely; however, if the Court were ever to deny review while the preliminary injunction remained live, one or more members of the five-Justice stay majority would be very likely to write a dissent or statement respecting the denial. Blending those two conditional denial scenarios yields `0.25`.
- **`order-writers`:**
  - Because Chief Justice Roberts (joined by Justices Sotomayor, Kagan, and Jackson) already authored a comprehensive 7-page dissent at the stay stage (`No. 26A203`, App. 10a–16a), if the Court grants, vacates, and remands in light of the stay opinion, the most likely outcome is either an unsigned order with no new separate opinion or a brief noted dissent referencing the stay dissent. We assign modest per-Justice probabilities (`Sotomayor: 0.07`, `Jackson: 0.07`, `Roberts: 0.06`, `Gorsuch: 0.06`, `Kavanaugh: 0.06`, `Thomas: 0.06`, `Alito: 0.05`, `Barrett: 0.05`, `Kagan: 0.03`) to account for the possibility of a brief concurrence or dissent accompanying the cert disposition order.
