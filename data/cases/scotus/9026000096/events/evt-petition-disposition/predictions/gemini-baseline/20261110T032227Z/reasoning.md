# Certiorari Prediction: *Department of the Interior, et al. v. Shoshone-Bannock Tribes of the Fort Hall Reservation, et al.*, No. 26-96

## I. Executive Summary

- **Prediction:** `granted = true` (`predicted_disposition = "granted"`)
- **Probability of Grant:** `0.67` (Disposition distribution: `granted: 0.67`, `denied: 0.30`, `gvr: 0.01`, `other: 0.02`)

This petition—filed by the Solicitor General on behalf of the Department of the Interior and the Bureau of Land Management (BLM), alongside a companion petition by intervenor J.R. Simplot Company (No. 26-109)—asks whether the Federal Land Policy and Management Act of 1976 (FLPMA), 43 U.S.C. §§ 1701 *et seq.*, authorizes BLM to conduct a public-land exchange involving former reservation lands ceded to the United States in 1898, notwithstanding Section 5 of the Act of June 6, 1900, ch. 813, 31 Stat. 672, 676 (which provided that the ceded lands "shall be subject to disposal under the homestead, town-site, stone and timber, and mining laws of the United States only").

Anchored to the empirical base rate for federal-petitioner (Solicitor General) certiorari petitions in `metrics/statpack.md` and `record/context.json` (**73.1%**, or 155 of 212 over OT2016–OT2025), I adjust slightly downward to **67%** to reflect non-trivial vehicle and posture headwinds—specifically, the absence of a circuit split, the interlocutory 28 U.S.C. § 1292(b) posture (with unreviewed alternative holdings by the district court under FLPMA and NEPA), and the possibility of congressional action in pending FY2027 NDAA legislation (S. 4784, § 1091(b)). However, those vehicle concerns are largely offset by powerful cert-grant signals: the Solicitor General's institutional backing, a coordinated companion petition by Miguel Estrada for J.R. Simplot (No. 26-109), five business and multi-state amicus briefs at the cert stage, and a sharp 7-judge dissent from the denial of rehearing en banc in the Ninth Circuit (authored by Judges Collins and Tung, joined by Judges Callahan, Bennett, R. Nelson, Bumatay, and VanDyke) highlighting both the doctrinal clash over statutory harmonization and the practical impact on federal public-land administration across the West.

---

## II. Base-Rate Anchor and Structural Signals

1. **Solicitor General / Federal Petitioner Anchor (`0.731`):**
   - Per `record/context.json` (`band: "federal"`) and `metrics/statpack.md` (*Cert grant base rates (OT2016–OT2025)*), petitions where the United States or a federal agency/officer represented by the Solicitor General is the petitioner are granted at a **73.1%** rate (155 / 212) over the 10-Term lookback window, and **81.0%** (17 / 21) in OT2025.
   - Even in the absence of a direct circuit conflict, the Court routinely grants federal petitions where a court of appeals has invalidated a significant federal agency action or restricted executive statutory authority over federal property and natural resources (e.g., *United States Forest Service v. Cowpasture River Preservation Ass'n*, 590 U.S. 604 (2020); *Andrus v. Utah*, 446 U.S. 500 (1980)).

2. **Companion Petition and Amicus Support:**
   - The case is paired (`Vide`) with *J.R. Simplot Company, LLC v. Shoshone-Bannock Tribes of the Fort Hall Reservation*, No. 26-109 (represented by Miguel Estrada), distributed on the same schedule for the December 4, 2026 conference.
   - Five amicus briefs were filed supporting petitioners at the certiorari stage:
     1. **States of Idaho, Nevada, and Utah (and their Governors)** — emphasizing state and regional economic reliance on predictable FLPMA land exchanges across western public-land states.
     2. **Chamber of Commerce of the United States of America** — emphasizing clouding of title and regulatory uncertainty for businesses operating on or exchanging public lands.
     3. **National Mining Association** — emphasizing the impact on mineral and land-use operations across public lands subject to 19th- and early-20th-century cession or disposal statutes.
     4. **National Association of Manufacturers and The Fertilizer Institute** — emphasizing the importance of the Don Plant to domestic phosphate fertilizer production and agricultural supply chains.
     5. **Mountain States Legal Foundation** — emphasizing FLPMA's structure and western public-land management.

3. **Lower-Court Division (Panel Dissent and 7-Judge En Banc Dissent):**
   - In the Ninth Circuit, Judge Friedland (joined by District Judge Kennelly, sitting by designation) affirmed the district court's summary judgment order invalidating the Blackrock Land Exchange. Judge Bumatay dissented in full on both the 1900 Act/FLPMA issue and the district court's alternative FLPMA/NEPA grounds.
   - On April 21, 2026, the Ninth Circuit denied rehearing en banc over two published dissents—one by Judge Collins and one by Judge Tung (joined by Judges Callahan, Bennett, R. Nelson, Bumatay, and VanDyke)—plus a separate statement by Judge Tung and a responsive statement by Judges Friedland and Kennelly. Seven active circuit judges dissenting from denial of rehearing en banc in the Ninth Circuit is a well-established signal that attracts close scrutiny from the Supreme Court's conservative majority.

---

## III. Merits and Doctrinal Appeal to the Court

The statutory question presented is clean, textual, and squarely aligned with the current Court's interest in statutory harmonization, anti-entrenchment principles, and the scope of Indian-law canons:

1. **Text and Structure of FLPMA vs. the 1900 Act:**
   - FLPMA authorizes BLM to exchange "public lands"—defined broadly as "any land and interest in land owned by the United States within the several States and administered by the Secretary of the Interior through the Bureau of Land Management, without regard to how the United States acquired ownership," subject to only two express exceptions (Outer Continental Shelf lands and lands held in trust/for the benefit of Indians, 43 U.S.C. § 1702(e)). Both sides and the panel majority agree that the ceded Fort Hall lands fall within FLPMA's definition of "public lands" and neither exception applies.
   - The panel majority nevertheless held that Section 5 of the 1900 Act—which provided that the residue of the ceded lands "shall be opened to settlement by the proclamation of the President, and shall be subject to disposal under the homestead, town-site, stone and timber, and mining laws of the United States only"—operates as a permanent, exclusive ceiling barring disposal under FLPMA because FLPMA (while repealing 251 statutes, including the 1926 Act specifically extending isolated-tract sales to the ceded Fort Hall lands) did not expressly repeal the 1900 Act and contains a general savings clause against implied repeals (§ 701(f), 90 Stat. 2786).
   - As the Solicitor General, Judge Bumatay, Judge Collins, and Judge Tung argue, reading "only" in the 1900 Act to bar later-enacted, comprehensive disposal mechanisms under FLPMA is in serious tension with *Epic Systems Corp. v. Lewis*, 584 U.S. 497, 510 (2018) (duty to harmonize statutes and give effect to both as coexisting grants of authority), and *Dorsey v. United States*, 567 U.S. 260, 274 (2012) (one Congress cannot entrench against or require "magical passwords" from a later Congress). Moreover, Judge Collins's en banc dissent highlights a particularly sharp textual point: FLPMA *expressly repealed* the 1926 Act (which applied exclusively to the ceded Fort Hall lands) in order to replace piecemeal disposal authorities with FLPMA's uniform disposal and exchange framework (43 U.S.C. § 1701(a)(10)).

2. **Indian-Law Clear-Statement Canon:**
   - The panel majority reinforced its holding by invoking the Indian-law clear-statement canon for abrogation of treaty rights (*Minnesota v. Mille Lacs Band*, 526 U.S. 172 (1999); *Herrera v. Wyoming*, 587 U.S. 329 (2019)), reasoning that because the 1898 Agreement reserved tribal hunting, fishing, timber, and grazing rights "[s]o long as any of the lands ceded ... remain part of the public domain," expanding the ways land can leave the public domain requires a clear statement.
   - The Solicitor General and the dissenters respond that the 1898 Agreement's usufructuary rights were expressly conditioned on the lands remaining in the public domain and conferred no treaty right restricting *how* the United States disposes of its public lands; Section 5 of the 1900 Act was unilateral congressional legislation, not part of the negotiated 1898 Agreement. Following *Arizona v. Navajo Nation*, 599 U.S. 555 (2023), the Court's majority has been skeptical of expansive applications of tribal trust and canon doctrines where the treaty text itself imposes no affirmative restriction on the government.

---

## IV. Vehicle, Posture, and Mootness Risks (Downward Adjustments)

Despite the strong federal-petitioner base rate (73.1%), three factors counsel a modest downward adjustment to **0.67**:

1. **Absence of a Circuit Split:**
   - The Solicitor General candidly does not claim a circuit conflict, and Simplot's reliance on *National Coal Ass'n v. Hodel*, 825 F.2d 523 (D.C. Cir. 1987), involves a statute (the Mineral Leasing Act) that expressly cross-referenced FLPMA §§ 206 and 209. Respondent's BIO (by Neal Katyal) effectively demonstrates that many of the 35 pre-FLPMA statutes cited by the government have textual differences from the 1900 Act. While a circuit split is not required for an SG petition on public-lands administration, its absence still reduces grant probability relative to SG petitions that resolve an active inter-circuit conflict.

2. **Interlocutory Posture and Alternative Holdings Below:**
   - The appeal reached the Ninth Circuit on interlocutory certification under 28 U.S.C. § 1292(b) before the district court adjudicated remedies. More importantly, the district court also ruled that the Blackrock Land Exchange violated FLPMA's appraisal rules (by not valuing the parcel for Simplot's gypstack use), FLPMA's public-interest cultural-resources requirement, and NEPA (by not evaluating preliminary gypstack/cooling-pond design alternatives). The Ninth Circuit panel majority declined to reach those three alternative grounds.
   - Respondent argues that a ruling on the 1900 Act would not be outcome-determinative because the exchange remains invalid on those alternative grounds. However, the SG and five dissenting Ninth Circuit judges persuasively respond that: (a) the 1900 Act holding is a permanent, categorical bar to the project, whereas any NEPA or FLPMA appraisal/explanation defects are procedural matters that could be cured on remand or reversed on appeal by the Ninth Circuit (especially after *Seven County Infrastructure Coalition v. Eagle County*, 605 U.S. 168 (2025)); and (b) the district court itself certified the order under § 1292(b) because whether the exchange is categorically illegal under the 1900 Act vs. procedurally defective under FLPMA/NEPA fundamentally alters the remedial inquiry (e.g., permanent vacatur and deed rescission vs. remand without vacatur).

3. **Pending Legislation (FY2027 NDAA, S. 4784, § 1091(b)):**
   - As noted in both the BIO (at 33) and the SG's Cert Reply (at 11), Section 1091(b) of the Senate's pending FY2027 National Defense Authorization Act (S. 4784) would expressly ratify the Blackrock Land Exchange "[n]otwithstanding any other provision of law."
   - The SG's reply brief notes that cloture on S. 4784 failed in July 2026 and the House counterpart (H.R. 8070) lacks the provision, making enactment uncertain; the SG further observes that the Court could reschedule the petition briefly to see whether Congress acts in the year-end NDAA and grant plenary review this Term if Congress does not ratify the exchange.
   - If Congress were to enact § 1091(b) before the Court acts on the petition (or if the Court holds/reschedules the petition and the NDAA passes in late December 2026), the petition could be mooted (`gvr` under *Munsingwear* or dismissed/`other`), or denied. At the distribution moment (for the December 4, 2026 conference), however, the most likely disposition of the petition remains a grant of certiorari (either immediately in December 2026 or after a brief relist/reschedule once the year-end NDAA omits the contested rider).

---

## V. Calibration and Final Probability Breakdown

- **Starting Anchor:** `0.731` (10-Term SG/federal petitioner cert grant rate).
- **Positive Adjustments:** Companion petition by major corporate intervenor represented by experienced Supreme Court counsel (`+0.03`), five cert-stage amicus briefs (`+0.03`), and a 7-judge Ninth Circuit en banc dissent on a statutory/Indian-canon question of high interest to the current Court (`+0.06`).
- **Negative Adjustments:** Lack of a square circuit split (`-0.06`), interlocutory § 1292(b) posture with unreviewed alternative holdings below (`-0.08`), and modest risk of legislative mootness or deferral due to the pending FY2027 NDAA rider (`-0.04`).
- **Net Estimate:**
  - `granted`: **0.67**
  - `denied`: **0.30**
  - `gvr`: **0.01** (small probability that Congress enacts the NDAA ratification prior to cert disposition, prompting a *Munsingwear* GVR)
  - `other`: **0.02** (small probability of dismissal/mootness disposition prior to a cert vote)
