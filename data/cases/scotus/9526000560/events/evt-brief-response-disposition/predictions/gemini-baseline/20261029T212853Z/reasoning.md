# Prediction Reasoning: *Markwayne Mullin, Secretary of Homeland Security, et al. v. Friends of the Ruidosa Church, et al.* (No. 26A560)

- **Case ID:** `scotus/9526000560`
- **Event ID:** `evt-brief-response-disposition` (`stage: interim`, `moment: response-filed`)
- **Predictor:** `gemini-baseline` (`gemini-4-argon`)
- **Snapshot Read:** `2026-10-29.json` (`mode: forward`, `cutoff: 2026-10-30`, `cut_kind: date`)
- **Forecast:** `granted: 1`, `probability: 0.85`, `predicted_disposition: "granted"`, `big_case_score: 0.78`

---

## 1. Inputs Consulted & Procedural Posture

This forecast is formed from the provisioned snapshot (`data/cases/scotus/9526000560/record/snapshots/2026-10-29.json`), `record/context.json`, and the two full party filings provisioned in `record/documents/` (`application.txt` [42 pages, no truncation] and `application-response.txt` [50 pages, no truncation]). As directed for an `interim` stage cell, I do not anchor on any cert-stage salience band (`band: null` in `context.json`), and instead anchor on the interim-docket base rate in `metrics/statpack.md` and adjust for the escalation-ladder signals and case-specific legal and equitable posture.

### Procedural Posture from the Provisioned Filings
Between February and July 2026, the Secretary of Homeland Security issued four notices of determination under Section 102(c) of the Illegal Immigration Reform and Immigrant Responsibility Act of 1996 (IIRIRA), Pub. L. No. 104-208, Div. C, 110 Stat. 3009-554 (8 U.S.C. § 1103 note), waiving 36 federal statutes (including NEPA, the Endangered Species Act, the Clean Water Act, the National Historic Preservation Act, and the APA) and state and local laws across 517 contiguous miles of the U.S.–Mexico border in the Big Bend Sector of West Texas (91 Fed. Reg. 7516 [Feb. 18, 2026]; 91 Fed. Reg. 20703 [May 6, 2026]; 91 Fed. Reg. 27968 [June 24, 2026]; 91 Fed. Reg. 29972 [July 9, 2026]).

Because IIRIRA § 102(c)(2)(A) strips district courts of jurisdiction over all non-constitutional claims arising from the Secretary's waivers ("a cause of action or claim may only be brought alleging a violation of the Constitution of the United States") and § 102(c)(2)(C) channels appellate review of any interlocutory or final district court order exclusively to the Supreme Court on writ of certiorari, respondents (Friends of the Ruidosa Church, Center for Biological Diversity, and rancher Danny William Miller Jr.) sued in the Western District of Texas (El Paso Division, Judge Kathleen Cardone) alleging that the waivers exceeded IIRIRA § 102(a) and § 102(c)(1) under the Major Questions Doctrine and thereby violated the Presentment Clauses, the Nondelegation Doctrine, and the Take Care Clause.

On October 2, 2026, the district court entered a one-page order granting a preliminary injunction without an opinion. After the government moved for a stay on October 8, the district court issued its memorandum opinion on October 14, 2026, holding that:
1. IIRIRA § 102(c)(1)'s waiver power applies only to "barriers and roads under this section" authorized by § 102(a) or § 102(b);
2. Under the Major Questions Doctrine, § 102(a)'s mandate to install "additional physical barriers and roads ... in the vicinity of the United States border to deter illegal crossings in areas of high illegal entry" must be narrowly construed to authorize only "gap-filling" barriers near existing urban fencing, not a 517-mile barrier across the remote Big Bend region;
3. Because the Secretary lacked statutory authority under § 102(a), waiving 36 statutes violated the Presentment Clauses and the Take Care Clause, giving rise to a "constitutional" claim within § 102(c)(2)(A)'s jurisdiction; and
4. The government is enjoined from taking any action in reliance on the four waivers across the entire 517-mile project area.

On October 20, 2026, the district court denied a stay pending certiorari. On October 21, 2026, Solicitor General D. John Sauer applied to Circuit Justice Alito for an emergency stay pending certiorari (or certiorari before judgment and summary reversal). Justice Alito called for a response due October 29, 2026 at 4 p.m. EDT. On October 29, 2026, respondents filed their opposition brief (`application-response.txt`) and Keep Big Bend Wild et al. filed an amicus brief opposing a stay.

---

## 2. Base-Rate Anchor (`metrics/statpack.md` — The Interim Docket)

Per `metrics/statpack.md` (*The interim docket (applications)*), the scored baseline for an interim cell in application-Term `2026` is the unweighted grant rate pooled over resolved substantive applications in the ten application-Terms strictly preceding `2026` (`2016 <= T < 2026`):
- **OT2025:** 17 granted / 226 resolved (`7.5%`, `unparsed: 0`)
- **OT2024:** 16 granted / 194 resolved (`8.2%`, `unparsed: 0`)
- **OT2023:** 18 granted / 127 resolved (`14.2%`, `unparsed: 0`)
- **OT2022:** 9 granted / 103 resolved (`8.7%`, `unparsed: 0`)
- **OT2021:** 30 granted / 120 resolved (`25.0%`, `unparsed: 0`)
- **OT2020:** 25 granted / 133 resolved (`18.8%`, `unparsed: 0`)
- **OT2019:** 12 granted / 119 resolved (`10.1%`, `unparsed: 0`)
- **OT2018:** 12 granted / 113 resolved (`10.6%`, `unparsed: 0`)
- **OT2017:** 12 granted / 124 resolved (`9.7%`, `unparsed: 1`)
- **OT2016:** 9 granted / 107 resolved (`8.4%`, `unparsed: 15`)

Summing across `T in [2016, 2025]`:
- **Total substantive resolved:** $226 + 194 + 127 + 103 + 120 + 133 + 119 + 113 + 124 + 107 = \mathbf{1,366}$ (clearing the `INTERIM_BASE_RATE_MIN_RESOLVED = 50` floor by a wide margin; `unparsed` is 0 in OT2018–OT2025, 1 in OT2017, and 15 in OT2016).
- **Total substantive granted:** $17 + 16 + 18 + 9 + 30 + 25 + 12 + 12 + 12 + 9 = \mathbf{160}$.
- **Strictly-prior 10-Term pooled substantive grant rate:** $160 / 1,366 = \mathbf{11.71\%}$ (`0.117`).

### Conditioning on the Escalation Ladder & Applicant Identity
As `metrics/statpack.md` notes, the raw `11.71%` substantive pool is dominated by private and capital stay applications that are summarily denied without a response request. Across the statpack's entire substantive slice ($n = 1,465$ resolved, 170 granted, `11.6%`), only 302 applications drew a response request and only 140 had amicus participation, yet virtually all 170 grants come from the subset where a response was requested and the application was referred to the full Court.

Here, two escalation rungs have already climbed on `2026-10-29.json`:
1. `response_requested: true` (Justice Alito called for a response on the day of docketing, October 21, 2026);
2. `amicus_briefs: 1` (Keep Big Bend Wild et al. filed on October 29, 2026).

Most importantly, **the applicant is the Solicitor General of the United States** seeking to stay a district court preliminary injunction blocking a flagship executive border-security construction program. In our `fedcourts query` check of OT2026 substantive applications brought by Solicitor General D. John Sauer where a response was requested or filed, the Court granted stays in *Trump v. California* (`26A124`), *National Park Service v. National Trust for Historic Preservation* (`26A203`), *Department of Homeland Security v. League of Women Voters* (`26A308`), *Department of Homeland Security v. D.V.D.* (`26A406`), and *FCC v. Brown* (`26A476`), while denying *Trump v. Kingdom* (`26A416`). Historically (including the border-wall stays in *Trump v. Sierra Club*, 588 U.S. 944 (2019), and *Trump v. Sierra Club*, 591 U.S. ___ (2020)) and in OT2025–OT2026, Solicitor General stay applications challenging injunctions against border/immigration or construction initiatives grant at **~80%–85%**.

---

## 3. Case-Specific Adjustments (*Nken* Factors)

Starting from the `11.7%` unconditioned interim base rate and the `~80%` empirical rate for Solicitor General stay applications with a requested response, I adjust upward to **0.85** (`P(unqualified grant) = 0.85`) for four reasons:

### A. Exclusive Supreme Court Appellate Jurisdiction (§ 102(c)(2)(C))
In an ordinary stay application, respondents can argue that the Supreme Court should let the court of appeals review the preliminary injunction first. Here, **IIRIRA § 102(c)(2)(C) eliminates court of appeals jurisdiction altogether**, providing that "[a]n interlocutory or final judgment, decree, or order of the district court may be reviewed only upon petition for a writ of certiorari to the Supreme Court of the United States." And while the Court previously denied certiorari when *environmental plaintiffs* sought review of lower-court decisions *upholding* § 102(c) waivers, this is the first case in history where a district court has **invalidated and enjoined** § 102(c) waivers. Because the Supreme Court is the sole appellate forum, the probability that at least four Justices will vote to grant certiorari if the injunction remains in effect is near 100%.

### B. Conflict with *Dalton v. Specter* on Jurisdiction-Stripping (§ 102(c)(2)(A))
IIRIRA § 102(c)(2)(A) restricts district court jurisdiction strictly to causes or claims "alleging a violation of the Constitution of the United States." The district court did not hold that § 102(c) violates the Nondelegation Doctrine or the Presentment Clauses on its face—every court to consider those facial constitutional challenges since 2005 has rejected them. Instead, the district court held that the Secretary's Big Bend waivers *exceeded his statutory authority* under § 102(a) and § 102(c)(1), and reasoned that waiving 36 statutes without statutory authority violates the Presentment Clauses and the Take Care Clause.

That holding squarely conflicts with *Dalton v. Specter*, 511 U.S. 462, 471–74 (1994), which held that an executive official's action in excess of statutory authority is a statutory *ultra vires* claim, not a constitutional separation-of-powers claim. As Judge Katsas explained in *Center for Biological Diversity v. McAleenan*, 404 F. Supp. 3d 218, 233–35 (D.D.C. 2019), and as the Ninth and D.C. Circuits held in *In re Border Infrastructure Environmental Litigation*, 915 F.3d 1213 (9th Cir. 2019), and *North American Butterfly Ass'n v. Wolf*, 977 F.3d 1244, 1262–63 (D.C. Cir. 2020), allowing plaintiffs to dress up statutory *ultra vires* claims as Presentment or Take Care Clause violations would nullify § 102(c)(2)(A)'s jurisdiction-stripping bar.

### C. Statutory Text of IIRIRA § 102(a), OBBBA ($46.5B), and the Major Questions Doctrine
Even if a court can examine whether the Big Bend projects qualify as "barriers and roads under this section" to trigger § 102(c)(1) and § 102(c)(2)(A), the district court's use of the Major Questions Doctrine to restrict § 102(a) to narrow "gap-filling" projects near existing urban barriers is highly likely to be rejected by a majority of the Court:
1. Section 102(a) broadly authorizes "additional physical barriers and roads (including the removal of obstacles to detection of illegal entrants) in the vicinity of the United States border to deter illegal crossings in areas of high illegal entry into the United States." In *Border Infrastructure*, 915 F.3d at 1224–25, the Ninth Circuit rejected the argument that § 102(a) is tethered to the specific priority segments in § 102(b).
2. Unlike executive actions that relied on oblique or ancillary statutory language (*Learning Resources, Inc. v. Trump*, 607 U.S. ___ (2026); *Biden v. Nebraska*, 600 U.S. 477 (2023)), IIRIRA § 102(c)(1) is an express, sweeping delegation ("Notwithstanding any other provision of law, the Secretary of Homeland Security shall have the authority to waive all legal requirements such Secretary, in such Secretary's sole discretion, determines necessary to ensure the expeditious construction of the barriers and roads under this section"), reinforced in July 2025 by Congress's **$46.5 billion** appropriation in the One Big Beautiful Bill Act (Pub. L. No. 119-21, § 90001(1)(A), 139 Stat. 357) for border barrier system construction.

### D. Remedial Overbreadth and *Trump v. CASA*
Just two months ago in *National Park Service v. National Trust for Historic Preservation* (`26A203`, Aug. 31, 2026), the Court granted a stay of a preliminary injunction halting federal construction, emphasizing threshold standing/remedial limits and citing *Trump v. CASA, Inc.*, 606 U.S. 831 (2025). Here, the district court enjoined reliance on four waivers across all **517 miles** of the Big Bend sector—halting road maintenance, cameras, and contract awards across hundreds of miles—even though respondents' declarations establish concrete injuries only at specific sites (the Ruidosa Church, Mr. Miller's ranch in Presidio County, and specific park areas visited by CBD members). Even if a Justice were sympathetic to a narrow as-applied challenge, the injunction's sector-wide sweep makes an unqualified stay pending cert the overwhelmingly likely outcome.

---

## 4. Uncertainties & Downside Risks (Why 0.85 Rather Than 0.95)

Two factors keep `probability` at **0.85** rather than higher:
1. **Imminent Summary Judgment Briefing Below:** Respondents emphasize (`application-response.txt` at 2, 16, 42–43) that expedited summary judgment briefing in the district court is already underway and concludes on **November 16, 2026**—just two and a half weeks away—and that CBP's own declarations state that actual physical wall construction in Ruidosa and Big Bend National Park was not scheduled to begin immediately (contracts for Big Bend phases were slated for award in late 2026 with construction in early 2027). There is roughly a **10%–12% chance** the Court denies the stay without prejudice to the government seeking relief once the district court enters final summary judgment in late November or December 2026.
2. **Risk of Partial Relief (`granted-in-part` Collapsing to `denied`):** Because the pipeline's interim resolver codes any mixed "granted in part and denied in part" order as `denied` (matching denial language first), I must discount for the small (~3%–5%) possibility that the Court stays the injunction as to the broader 517-mile sector (or as to road maintenance and technological barriers) while leaving it in place strictly as to physical wall construction on Mr. Miller's property or in Ruidosa pending summary judgment. However, because the *Dalton v. Specter* / § 102(c)(2)(A) jurisdictional defect applies equally to the entire suit, an **unqualified stay grant (`0.85`)** is far more probable than a tailored partial stay.

---

## 5. Rationale for Other Declared Claims, Votes, and `big_case_score`

- **`claims` (`interim-v2`):**
  - `interim-disposition`: `0.85` (matches top-level `probability`).
  - `response-requested-increment`: `0.0` (`response_requested` is already `true` in `context.json`; vacuous).
  - `referral-increment`: `0.97` (`referred_to_court` is currently `false`; Circuit Justice Alito almost always refers contested Solicitor General stay applications to the full Court once the response is filed).
  - `amicus-increment`: `0.35` (`amicus_briefs` is currently `1`; because the October 29 response deadline has arrived, most amici have already filed, though there remains a 35% chance of a late submission by Texas or an ideological amicus before the order issues).
- **`claim_distributions` (`order-writers`):**
  - Most interim stay orders issue without a signed or *per curiam* opinion (around 65% probability of no opinion, or noted dissents only). If a separate writing is published, the likeliest authors are Justice Sotomayor (`0.22`) or Justice Jackson (`0.22`) dissenting from the grant of the stay (as in *DHS v. League of Women Voters*, `26A308`, and *National Park Service v. National Trust*, `26A203`), followed by Justice Kagan (`0.08`), Justice Kavanaugh (`0.08`), and Justice Gorsuch (`0.06`).
- **`big_case_score`: `0.78`:**
  - The case is high-stakes both practically and doctrinally: it involves the construction of a 517-mile border barrier through iconic public lands (Big Bend National Park and Big Bend Ranch State Park) backed by a $46.5 billion congressional appropriation, and presents the first judicial invalidation of an IIRIRA § 102(c) waiver in two decades alongside a direct test of whether the Major Questions Doctrine can overcome statutory jurisdiction-stripping under *Dalton v. Specter*.

*Note on retrieval:* All core precedents and the full provisioned briefs were read. On the final two CourtListener MCP calls seeking lower-court RECAP docket entries from W.D. Tex. after reading the opinions, the CourtListener API returned a daily rate-limit error (HTTP 429); because the provisioned `application.txt` and `application-response.txt` already thoroughly summarize the district court's October 14, 2026 opinion and October 20, 2026 stay denial, this had no impact on the forecast.
