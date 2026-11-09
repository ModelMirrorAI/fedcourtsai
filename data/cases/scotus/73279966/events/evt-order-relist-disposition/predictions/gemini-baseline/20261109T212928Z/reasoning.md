# Certiorari Disposition Rationale — *The GEO Group, Inc. v. Ugochukwu Nwauzor, et al.*, No. 25-828 (`evt-order-relist-disposition`)

## 1. Summary of Numbers

- **`granted`:** `1` (`predicted_disposition: "granted"`)
- **`probability` (`disposition`):** `0.72`
- **`big_case_score`:** `0.78`
- **Declared `claims` (`cert-v3`):**
  - `disposition`: `0.72`
  - `relist-increment`: `0.35`
  - `cvsg-increment`: `0.01` (vacuous; CVSG already issued on May 18, 2026)
  - `summary-disposition-route`: `0.04` (conditional on grant)
  - `dissent-from-denial`: `0.42` (conditional on denial)
- **Declared `claim_distributions` (`order-writers`):**
  - `Alito`: `0.08`, `Thomas`: `0.07`, `Gorsuch`: `0.06`, `Sotomayor`: `0.02`, `Kavanaugh`: `0.02`, `Jackson`: `0.02`, `Roberts`: `0.01`, `Kagan`: `0.01`, `Barrett`: `0.01`

---

## 2. Provisioned Inputs Consulted

All provisioned files under `data/cases/scotus/73279966/record/` were read and weighed:
- **Snapshot:** `record/snapshots/2026-11-09.json` (`input_snapshot: "2026-11-09.json"`) and `record/context.json` (`mode: "forward"`, `band: "high"`, `salience_version: "sal-v8"`, `distribution_count: 3`, `cvsg_date: "2026-05-18"`, `term: 2025`, `cutoff: "2026-11-09"`, `cut_kind: "date"`).
- **Provisioned Filings (`record/documents/`):**
  - `questions-presented.txt` and `petition.txt` (GEO Group's petition filed by Paul D. Clement presenting three Supremacy Clause questions: direct-regulation intergovernmental immunity, discriminatory intergovernmental immunity, and federal preemption).
  - `brief-in-opposition.txt` (containing both the State of Washington's BIO filed Apr. 9, 2026 and Individual Respondents Nwauzor et al.'s BIO resubmitted Apr. 10, 2026, plus trial excerpts and ICE-GEO contract excerpts).
  - `cert-reply.txt` (GEO Group's reply brief filed Apr. 27, 2026, addressing *Hencely v. Fluor Corp.* and *GEO Group, Inc. v. Menocal*).
  - `sg-invited-brief.txt` (Brief for the United States as Amicus Curiae filed Sept. 14, 2026 by Solicitor General D. John Sauer in response to the Court's May 18, 2026 CVSG, recommending **without qualification that the petition for a writ of certiorari be granted**).
  - `supplemental-brief.txt` (combined supplemental briefs of Respondent State of Washington and Individual Respondents Nwauzor et al., both filed Sept. 29, 2026).
  - `decision-below.txt` and `lower-court-docket.txt` (the Ninth Circuit's published decision in *Nwauzor v. The GEO Group, Inc.*, 127 F.4th 750 (9th Cir. Jan. 16, 2025), with Judge W. Fletcher's majority opinion and Judge Bennett's dissent, and the August 13, 2025 order denying rehearing en banc over a noted dissent, 146 F.4th 1280).

---

## 3. Base-Rate Anchor and Statistical Calibration

1. **Frozen Salience-Band Anchor (`record/context.json` & `metrics/statpack.md`):**
   - `record/context.json` freezes `band: "high"` under `salience_version: "sal-v8"` and provides the pre-pooled `cert_anchor`:
     - **`cert_anchor.rate = 0.3455056179775281` (34.55%)**, pooled over `lookback_terms = 10` (Terms `2016`–`2024`, strictly preceding `term: 2025`), representing `246.0` weighted grants out of `712.0` weighted resolved petitions in the `high` band's risk set.
   - In `metrics/statpack.md`, the `high` band's bracketed `reached` grant-family rates in the most recent strictly-prior Terms were `43.2% (n=95)` in OT2024, `26.5% (n=83)` in OT2023, and `34.1% (n=82)` in OT2022 (and `38.3% (n=60)` in OT2025).
2. **Cross-Checking the Statpack Signal Cuts (`metrics/statpack.md`):**
   - **Relist count cut (paid scored segment):** Pooling buckets `1` (`n=2532`, granted `8.3%`, gvr `5.2%` → `13.5%` grant family), `2` (`n=495`, granted `28.3%`, gvr `12.9%` → `41.2%` grant family), and `3+` (`n=483`, granted `23.2%`, gvr `14.1%` → `37.3%` grant family) gives `722` grant-family resolutions out of `3510` resolved relisted petitions (`20.6%` across `1+`, and **`39.3%`** across `2+` (`400 / 978`), which is where `distribution_count = 3` sits).
   - **CVSG cut (paid scored segment):** Across all `cvsg` petitions (`n=164` resolved), `29.3%` were granted and `5.5%` were GVR'd (**`34.8%` grant family**; `62.8%` denied, `2.4%` dismissed), compared to `6.4%` grant family (`4.1%` granted, `2.3%` gvr, `n=13550`) for non-CVSG petitions.
   - **Amicus-brief count cut (paid scored segment):** The docket records 5 pre-disposition amicus briefs (Immigration Reform Law Institute, Customized Distribution Services, Human Rights Defense Center, American Federation of Labor and Congress of Industrial Organizations, and the United States' invited brief), placing this case well into the `2+` bucket (`n=1446` resolved: `18.2%` granted, `4.5%` gvr → `22.7%` grant family).
   - **Originating circuit cut:** Ninth Circuit (`ca9`, `n=5615` resolved in modern cert petitions: `2.1%` granted, `1.2%` gvr).
3. **Why the SG's Grant Recommendation Moves the Forecast Sharply Above 0.3455:**
   - The `0.3455` `high`-band base rate and the `34.8%` `cvsg` cut pool *all* CVSG petitions regardless of what the Solicitor General recommends. Empirically, the Solicitor General recommends *denial* in roughly 70–75% of CVSG briefs (where the Court follows the SG and denies review ~85–90% of the time), whereas in the ~20–25% of CVSGs where the Solicitor General recommends a **plenary grant**, the Court grants certiorari roughly 70–80% of the time.
   - Here (`sg-invited-brief.txt`, pp. 1, 9, 24), Solicitor General Sauer states unequivocally: *"In the view of the United States, the petition for a writ of certiorari should be granted."* That recommendation is the single strongest upward shifter from the `0.3455` anchor.

---

## 4. Case-Specific Weighing: Petition, SG Brief, BIOs, and Supplemental Briefs

### A. Upward Adjustments (+0.375 net above the 0.3455 anchor)

1. **Unqualified SG Support on Both Constitutional Grounds (`sg-invited-brief.txt`):**
   - The United States endorses *both* of GEO's primary constitutional challenges:
     - **Intergovernmental Immunity — Discrimination & Direct Regulation (SG Br. 10–16):** Washington's MWA expressly exempts "[a]ny resident, inmate, or patient of a state, county, or municipal correctional, detention, treatment or rehabilitative institution," Wash. Rev. Code § 49.46.010(4)(k), where state inmates earn at most $40/week, while Washington simultaneously prohibits its Department of Corrections from contracting with private correctional entities (Wash. Rev. Code § 72.68.110(1)). As a result, GEO's Tacoma NWIPC is the *only* secure adult detention facility in Washington required to pay detainees the state minimum wage (>$17/hour). Moreover, detaining noncitizens pending removal decisions is an exclusively federal function, and the Washington Supreme Court departed from its longstanding "economic-dependence" test specifically to bring NWIPC detainees within the MWA.
     - **Conflict / Obstacle Preemption (SG Br. 16–19):** Under 8 U.S.C. §§ 1231(g)(1) and 1555(d) (and the 1979 Appropriations Act setting the $1/day allowance cap), Congress vested authority over detainee work allowances in the DHS Secretary within congressional appropriations limits. Imposing a state minimum wage more than 100 times the $1/day federal rate upends the federal scheme and directly caused the suspension of the VWP at NWIPC in October 2021.
   - Continuity across administrations: As the SG notes (SG Br. 2, 9), the United States has filed amicus briefs supporting GEO's Supremacy Clause defenses in this litigation across multiple presidential administrations.

2. **Circuit Split and Deep En Banc Division Below (`decision-below.txt`, `petition.txt`, `sg-invited-brief.txt`):**
   - Both the SG (SG Br. 9–10, 19–21) and petitioner (Pet. 19–25) argue that the Ninth Circuit's decision conflicts with the Third Circuit's decision in *CoreCivic, Inc. v. Governor of New Jersey*, 145 F.4th 315 (3d Cir. 2025) (Bibas, J.), which held that a facially neutral state law regulating private immigration detention contracts violates intergovernmental immunity because only the federal government detains noncitizens for civil immigration violations, as well as with *United States v. Town of Windsor*, 765 F.2d 16 (2d Cir. 1985), *United States v. Virginia*, 139 F.3d 984 (4th Cir. 1998), and the Ninth Circuit's own en banc decision in *The GEO Group, Inc. v. Newsom*, 50 F.4th 745 (9th Cir. 2022).
   - Seven active Ninth Circuit judges dissented from the denial of rehearing en banc in this case (146 F.4th 1280), with comprehensive dissents by Judge Bennett (panel dissent, 127 F.4th at 767–80), Judge Bumatay, and Judge Collins.

3. **Synchronized Relist with Companion Petition *GEO Group v. Ferguson*, No. 26-71:**
   - Using `uv run fedcourts query --court scotus --docket-number 26-71`, I verified that GEO's companion petition from the Ninth Circuit (*The GEO Group, Inc. v. Ferguson* (formerly *Inslee*), No. 26-71, challenging Washington's HB 1470 inspection/operations regime targeting NWIPC, 151 F.4th 1107 / 166 F.4th 1188 (9th Cir. Feb. 11, 2026), where 8 judges dissented from denial of rehearing en banc) is also at `distribution_count = 3` and is scheduled for the exact same **November 13, 2026** conference.
   - This explains the timing gap between No. 25-828's September 30, 2026 distribution (for the Oct. 16 conference) and its November 4/9 redistribution and relist: the Court held No. 25-828 so that No. 25-828 and No. 26-71 could be considered together at the November 6 conference and relisted together for the November 13 conference.

4. **Clean Final-Judgment Posture:**
   - Unlike No. 26-71 (which arises from an interlocutory vacatur of a preliminary injunction and remand), No. 25-828 comes to the Court on a final judgment after jury and bench trials (~$37 million total exposure including $17.29M back pay, $5.95M unjust enrichment, fee awards, and interest, plus a permanent injunction that halted the VWP at NWIPC) and after certification of state-law questions to the Washington Supreme Court.

### B. Downward Adjustments and Uncertainties (Why `probability` is 0.72 rather than >0.85)

1. **ICE's June 2026 Revised National Detention Standards (`supplemental-brief.txt`):**
   - In their September 29, 2026 supplemental brief (Indiv. Resp. Supp. Br. 1–2, 9–11), the individual respondents highlighted a material intervening administrative development that the SG's brief did not mention: in June 2026, ICE issued revised National Detention Standards (Standard 5.6, at 182–84 (2026)) that now expressly *forbid* detention contractors from paying detained workers wages "exceeding the amount Congressionally allocated to ICE for reimbursing contract facilities in support of the Voluntary Work Program" ($1/day) and declare that detained workers "are not entitled to wages or benefits under applicable wage laws or labor regulations."
   - Because the Ninth Circuit's preemption and direct-regulation analysis turned heavily on the fact that the 2011 PBNDS only set a floor ("at least $1.00 (USD) per day") and GEO's prior contract required compliance with "applicable federal, state and local labor laws and codes," respondents argue that the 2011 PBNDS and contract are outdated and that this case has limited prospective significance. While the $37M judgment and ongoing NWIPC injunction keep the case live and high-stakes, this regulatory change gives cert-skeptical Justices a plausible vehicle objection on the preemption and direct-regulation questions.

2. **Tension with *Hencely v. Fluor Corp.* and *GEO Group, Inc. v. Menocal* (`supplemental-brief.txt`, `cert-reply.txt`):**
   - Washington's supplemental brief (State Supp. Br. 1–7) relies heavily on the Court's April 22, 2026 decision in *Hencely v. Fluor Corp.*, 146 S. Ct. 1086 (2026) (which I also checked via CourtListener MCP `opinion_id: 11314033`), and *The GEO Group, Inc. v. Menocal*, 607 U.S. 438 (2026). Although *Hencely* involved FTCA combatant-activities preemption rather than Supremacy Clause intergovernmental immunity, its broad language reiterating that private service contractors "do not perform governmental functions" and that states may generally regulate contractors unless federal law or contract instructions conflict could make some Justices cautious about GEO's broadest "direct regulation" theory.
   - Respondents also point to trial stipulations (`brief-in-opposition.txt`, pp. 6a–8a; State Supp. Br. 8–9) that Washington contracts with private entities to operate nine work-release and residential civil-commitment facilities under Wash. Rev. Code § 72.68.110(2) where residents are paid minimum wage, disputing the SG's premise that no privately operated state detention facilities exist in Washington.

3. **Vehicle Competition / Hold Risk with Companion Petition No. 26-71:**
   - Because No. 26-71 (*GEO Group v. Ferguson*) is relisted alongside No. 25-828 for the November 13, 2026 conference and challenges a Washington statute (HB 1470) that explicitly targets "private detention facilities" without the 2011 PBNDS / June 2026 Revised NDS contract complication, there is a small chance the Court grants No. 26-71 alone and holds No. 25-828 pending No. 26-71 (which would ultimately resolve No. 25-828 by GVR or grant after No. 26-71 is decided). However, because the Court already invested a CVSG in No. 25-828, has a forceful SG grant brief in No. 25-828, and No. 25-828 is on a final judgment rather than an interlocutory remand, granting No. 25-828 (either alone while holding No. 26-71, or alongside No. 26-71) is substantially more likely.

---

## 5. Rationale for Secondary Claims, `order-writers`, and `big_case_score`

- **`relist-increment` (`0.35`):** The petition is already at `distribution_count = 3` (and at its first true post-CVSG relist). In the majority of post-CVSG relists where the SG recommends a grant, the Court grants certiorari at the next conference (`0.65` chance of resolving on the Nov. 13, 2026 conference order list without another distribution). However, because No. 25-828 and No. 26-71 are being coordinated—and because a denial would likely draw a written dissent from denial requiring circulation—I assign a `0.35` probability to at least one additional distribution past `3`.
- **`cvsg-increment` (`0.01`):** A CVSG was already ordered on May 18, 2026 (`cvsg_date: "2026-05-18"`) and answered on September 14, 2026; the claim is vacuous by construction.
- **`summary-disposition-route` (`0.04`):** Conditional on a grant, plenary review is overwhelmingly likely (`0.96`). Neither petitioner nor the SG requested summary reversal or a GVR, and no intervening precedent supports vacating the Ninth Circuit's affirmance without plenary briefing.
- **`dissent-from-denial` (`0.42`) and `order-writers`:** Conditional on the `0.28` chance of denial, a noted or written dissent from denial is quite plausible (`0.42`), given the SG's strong recommendation to grant, the ~$37M final judgment and injunction halting the NWIPC Voluntary Work Program, and the forceful dissents below by Judges Bennett, Bumatay, and Collins. Unconditionally across all cert-order dispositions (`order-writers`, where a grant order carries no separate writing), the Justices most likely to author a dissent from denial are Justice Alito (`0.08`), Justice Thomas (`0.07`), and Justice Gorsuch (`0.06`), with much lower probabilities (`0.01`–`0.02`) for the remaining Justices.
- **`big_case_score` (`0.78`):** Decoupled from grant likelihood, a decision on the merits here will define the constitutional boundary between state labor/regulatory power and federal immigration-detention contracting nationwide—an issue of high legal, fiscal, and operational significance (`0.78`).
