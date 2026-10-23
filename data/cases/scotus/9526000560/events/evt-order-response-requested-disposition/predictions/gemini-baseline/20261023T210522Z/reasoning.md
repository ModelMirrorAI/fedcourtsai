# Prediction Rationale (`reasoning.md`): *Markwayne Mullin, Secretary of Homeland Security, et al. v. Friends of the Ruidosa Church, et al.* (No. 26A560)

- **Cell**: `scotus/9526000560` / `evt-order-response-requested-disposition` (`stage: interim`, `moment: response-requested`, `mode: forward`)
- **Input Snapshot**: `2026-10-23.json` (plus provisioned `application.txt` and `context.json`)
- **Headline Forecast**: `probability = 0.75` (`granted = 1`, `predicted_disposition = "granted"`)
- **Declared `interim-v1` Claims**:
  - `interim-disposition`: `0.75`
  - `response-requested-increment`: `0.00` (vacuous; response already requested Oct. 22, 2026)
  - `referral-increment`: `0.96`
  - `amicus-increment`: `0.85`
- **Big Case Score**: `0.78`

---

## 1. Base-Rate Anchoring (`metrics/statpack.md` — Interim Docket)

Because this is an **interim-stage** cell (`event.yaml`: `stage: interim`, `moment: response-requested`), `record/context.json` carries `band: null`, `term: 2026`, `response_requested: true`, `referred_to_court: false`, and `amicus_briefs: 0`. Per the interim-stage contract in `.github/prompts/predict.md`, we do not use the cert salience-band table; instead, we anchor on **"The interim docket (applications)"** section of `metrics/statpack.md`.

### A. Strictly-Prior Pooled Substantive Grant Rate
Pooling the per-Term `resolved (subst.)` and `granted` counts across application-Terms strictly before `term: 2026` within the ten-Term window (`2016 <= T < 2026`) from `metrics/statpack.md`:
- **OT2025**: `17` granted / `226` resolved substantive applications (`7.5%`, `unparsed: 0`)
- **OT2024**: `16` granted / `194` resolved substantive applications (`8.2%`, `unparsed: 0`)
- **OT2023**: `18` granted / `127` resolved substantive applications (`14.2%`, `unparsed: 0`)
- **OT2016–OT2022**: `0` resolved substantive applications (`unparsed` = 100% of applications in those Terms; the live poller's parsed coverage begins in OT2023).

Summing over `2016 <= T < 2026`:
- **Pooled Resolved Substantive Applications**: `226 + 194 + 127 = 547` (which clears `INTERIM_BASE_RATE_MIN_RESOLVED = 50`).
- **Pooled Substantive Grants**: `17 + 16 + 18 = 51`.
- **Strictly-Prior Pooled Interim Base Rate**: `51 / 547 = 9.32%` (`0.0932`).

### B. Accounting for Escalation Selection and Solicitor General Posture
As `metrics/statpack.md` and `.github/prompts/predict.md` caution, the `9.32%` baseline is unconditioned on the escalation ladder: it pools all resolved substantive applications, the vast majority of which are *pro se* or private stay applications denied by a Circuit Justice without calling for a response. Here:
1. **Response Requested (`response_requested: true`)**: Across the substantive slice in `statpack.md`, only 129 of 642 applications (`20.1%`) ever drew a response request (`27/227` in OT2025, `47/194` in OT2024, `36/127` in OT2023), while virtually all 60 substantive grants came from that response-requested subset (producing a conditional grant rate of roughly `45–50%` across all applicants once a response is requested).
2. **Solicitor General Applications in OT2025–OT2026**: Querying the corpus via `fedcourts query --court scotus --include-applications` shows that when the Solicitor General seeks a stay of a lower-court injunction barring implementation of a federal policy or construction project and the Court requests a response, the Court has granted relief in the overwhelming majority of cases—including in OT2026:
   - *Donald J. Trump v. California*, No. 26A124 (decided Aug. 24, 2026): **Granted** (6–3, staying injunction against Presidential election-integrity directive).
   - *National Park Service v. National Trust for Historic Preservation*, No. 26A203 (decided Aug. 31, 2026): **Granted** (5–4, staying injunction against White House East Wing demolition/construction).
   - *Department of Homeland Security v. League of Women Voters*, No. 26A308 (decided Sept. 25, 2026): **Granted** (6–3, staying vacatur of DHS SAVE program changes).
   - *Federal Communications Commission v. Brown*, No. 26A476 (decided Oct. 14, 2026): **Granted** (7–2, staying Fourth Circuit mandamus order).
   - By contrast, the rare Solicitor General stay denial in OT2026—*Trump v. Kingdom*, No. 26A416 (denied Oct. 21, 2026)—concerned a temporary 90-day rolling preliminary injunction under the Prison Litigation Reform Act where the D.C. Circuit had already expedited merits review and held that the government forfeited its statutory expiration argument.

3. **Crucial Scoring Rule — Denial-First Collapse on Partial Grants**:
   Under `.github/prompts/predict.md` (*Stage: interim*), `probability` is **P(the disposing entry reads as an unqualified grant)**, because the interim resolver matches denial language first and collapses a mixed `"granted in part and denied in part"` order into `denied` / ungranted. Thus, we must separate our belief in a **full, unqualified stay** (`0.75`) from the probability that the Court grants only a **partial stay** (`~0.13`, e.g., staying the 300-mile sector-wide injunction under *Trump v. CASA, Inc.* while leaving the injunction intact solely as to the immediate property of the historic Ruidosa Church) or denies the stay outright (`~0.12`).

---

## 2. Case-Specific Analysis of the Provisioned Record & District Court Filings

We read the provisioned `2026-10-23.json` snapshot, `context.json`, and the 39-page `record/documents/application.txt` (Solicitor General D. John Sauer's Application for a Stay of the Injunction Entered by the U.S. District Court for the Western District of Texas, filed Oct. 21, 2026). Because this cell runs in `forward` mode, we also used the CourtListener MCP server to read the district court's underlying October 14, 2026 Memorandum Opinion and Order (`Doc. 75`), respondents' opposition to the government's motion for a stay pending appeal (`Doc. 76`), and the district court's October 20, 2026 Order denying a stay (`Doc. 78`) in *Friends of the Ruidosa Church v. Mullin*, No. 3:26-cv-01099-KC (W.D. Tex.).

### A. Why a Full Stay (`granted`) Is Strongly Favored (`P = 0.75`)

1. **Exclusive Appellate Review in the Supreme Court Under IIRIRA § 102(c)(2)(C)**:
   Under Section 102(c)(2)(A) and (C) of IIRIRA (8 U.S.C. § 1103 note), federal district courts have exclusive original jurisdiction over claims arising from the Secretary's § 102(c)(1) border-barrier waivers, and *"An interlocutory or final judgment, decree, or order of the district court may be reviewed only upon petition for a writ of certiorari to the Supreme Court of the United States."* Because the Fifth Circuit has no jurisdiction to review or stay Judge Cardone's injunction, the Supreme Court does not act against the backdrop of an appellate denial; it is the *only* reviewing court capable of checking a single district judge's injunction halting $4.5 billion in federal construction across 300 miles of the international border.

2. **Express Jurisdiction-Stripping Bar on Non-Constitutional Claims (§ 102(c)(2)(A))**:
   Section 102(c)(2)(A) states: *"A cause of action or claim may only be brought alleging a violation of the Constitution of the United States. The court shall not have jurisdiction to hear any claim not specified in this subparagraph."*
   - Although respondents pleaded constitutional nondelegation and separation-of-powers claims in their complaint, they moved for—and the district court granted—a preliminary injunction *solely* on their non-constitutional *ultra vires* statutory claim that the Secretary failed to satisfy the statutory predicates of § 102(a) ("areas of high illegal entry") and § 102(b) ("Smart Wall" system).
   - Just four months ago, in *Mullin v. Doe*, No. 25-1083 (U.S. June 25, 2026), a 6–3 majority (Alito, J., joined by Roberts, C.J., and Thomas, Gorsuch, Kavanaugh, and Barrett, JJ.) reversed a lower court that had read the TPS judicial-review bar (8 U.S.C. § 1254a(b)(5)(A)) to permit review of statutory prerequisites, holding that the plain text of the immigration review bar foreclosed *all* non-constitutional claims.
   - Similarly, in *In re Border Infrastructure Environmental Litigation*, 915 F.3d 1213, 1221–26 (9th Cir. 2019), the Ninth Circuit squarely held that § 102(c)(2)(A) bars non-constitutional *ultra vires* claims alleging that border-barrier projects fail to comply with § 102(a) or (b). And under *Dalton v. Specter*, 511 U.S. 462, 472–77 (1994), an allegation that an executive official acted in excess of statutory authority cannot be recast as a constitutional separation-of-powers claim to evade a statutory bar on judicial review.

3. **Weakness of the District Court's Major-Questions Rationale**:
   In its October 14 opinion (`Doc. 75`), the district court relied heavily on *Learning Resources, Inc. v. Trump*, No. 24-1287 (U.S. Feb. 20, 2026), to apply a major-questions "clear-statement rule" to DHS's border-wall authority under § 102(a)–(b). That reasoning is unlikely to persuade a Supreme Court majority:
   - In *Learning Resources*, only three Justices (Roberts, C.J., Gorsuch, and Barrett, JJ.) joined the major-questions section (Part II-A-2), and the Court rejected tariffs under IEEPA because IEEPA never mentioned tariffs or duties.
   - Here, by contrast, IIRIRA § 102(a) expressly directs the Secretary to "install additional physical barriers and roads . . . in the vicinity of the United States border to deter illegal crossings," § 102(c)(1) expressly empowers the Secretary "in such Secretary's sole discretion" to "waive all legal requirements" to ensure expeditious construction, and Congress in July 2025 enacted the One Big Beautiful Bill Act (OBBBA), Pub. L. No. 119-21, § 90001(1), 139 Stat. 357, appropriating **$46.55 billion** specifically for CBP to construct "new or replacement primary, waterborne, and secondary border barrier system."
   - Whether fortifying the Big Bend and El Paso Sectors is necessary to deter illegal crossings and prevent traffic displacement from adjacent fortified sectors is a quintessential operational judgment committed to the Executive, and § 102(b)(3) expressly provides that nothing in subsection (b) requires the Secretary to install every listed technology component in any particular location.

4. **Sector-Wide Overbreadth Under *Trump v. CASA, Inc.* and Irreparable Harm**:
   The district court enjoined all land clearing and construction of barriers, roads, and lighting across the entire **300-mile** span of the El Paso and Big Bend Sectors, even though respondents' declarations establish standing only at discrete sites (the historic Ruidosa Church in Presidio County, river canyons in Big Bend National Park, and specific properties near the Chinati Mountains). Under *Trump v. CASA, Inc.*, 606 U.S. 831 (2025), a district court lacks equitable authority to enjoin federal action beyond what is necessary to provide complete relief to the plaintiffs with standing. Moreover, CBP's declarations show that the injunction is costing the government **$173,000 per day** in contractor standby charges across $4.5 billion in contracts—a concrete financial and sovereign injury that, under *National Park Service v. National Trust for Historic Preservation*, No. 26A203 (U.S. Aug. 31, 2026), and *Winter v. Natural Resources Defense Council, Inc.*, 555 U.S. 7 (2008), tilts the equities decisively toward the government.

### B. Downside Risks & Why `probability` Is `0.75` Rather Than `0.85+`

Two main risks account for the remaining `0.25` probability mass (`~0.13` risk of a mixed `granted in part and denied in part` order that scores as `0` under the interim denial-first collapse, plus `~0.12` risk of an outright denial):
1. **Risk of a Partial Stay Carve-Out for Ruidosa Church / Discrete Parcels (`~0.13`)**:
   Because the interim resolver scores `"Application for stay granted in part and denied in part"` as `denied` (`0`), any localized carve-out reduces `interim-disposition` to `0`. While the government's jurisdictional argument under § 102(c)(2)(A) sweeps across the entire *ultra vires* claim (favoring a clean, unqualified stay), there is a meaningful chance that five or more Justices choose to stay the injunction across the 300 miles of the El Paso and Big Bend Sectors *except* as to the immediate property of the historic Ruidosa Church (where plaintiffs also raised religious-exercise and historic-preservation concerns and where construction within 55 feet could cause irreversible structural collapse before certiorari is resolved).
2. **Government's Forfeiture of Substantive Merits Arguments in the District Court (`~0.12` outright denial)**:
   As Judge Cardone emphasized in both her October 14 opinion (`Doc. 75` at 7–8) and her October 20 stay denial (`Doc. 78` at 3–4), the government's preliminary-injunction opposition brief rested *exclusively* on § 102(c)(2)(A)'s jurisdictional bar and failed to advance any substantive defense of how the Big Bend waivers satisfied § 102(a) and (b) until its post-injunction motion for a stay. While subject-matter jurisdiction cannot be forfeited and the Court recently overlooked a similar forfeiture protest in *Department of Homeland Security v. League of Women Voters*, No. 26A308 (U.S. Sept. 25, 2026), if two conservative Justices conclude that § 102(c)(2)(A) does not preclude threshold review of whether a project falls within § 102(a), the government's thin record below and the irreversible nature of blasting in Big Bend National Park could lead the Court to deny a stay while expediting certiorari.

---

## 3. Justification for Procedural Increment Claims & Big Case Score

- **`response-requested-increment = 0.00`**: Justice Alito already requested a response on October 22, 2026 (`context.response_requested = true`), so this claim will be masked as vacuous at evaluation.
- **`referral-increment = 0.96`**: Every high-salience Solicitor General stay application in OT2025–OT2026 in which a response was requested (`26A124`, `26A203`, `26A308`, `26A416`, `26A476`) was referred by the Circuit Justice to the full Court. Only a sudden settlement, withdrawal, or mootness event (~4%) would prevent referral.
- **`amicus-increment = 0.85`**: In `context.json`, `amicus_briefs` is currently `0`. Given the six-day briefing window (Oct. 22–28, 2026) and the high visibility of Big Bend border-wall construction, it is very likely (`0.85`) that at least one amicus curiae brief will be submitted (which counts toward the increment even prior to formal leave-granting).
- **`big_case_score = 0.78`**: This dispute implicates $4.5 billion in border-barrier contracts under the flagship 2025 OBBBA appropriation, 300 miles of the southwest border including Big Bend National Park, the scope of immigration/border jurisdiction-stripping provisions after *Mullin v. Doe*, and the reach of the major questions doctrine after *Learning Resources v. Trump*.
