# Certiorari Arrival Prediction Rationale: *Kenneth Genalo, et al. v. D. C.*, No. 26-379

## 1. Summary of Numbers
- **`granted`**: `1` (`predicted_disposition: "granted"`)
- **`probability`**: `0.88` (plenary grant ~`0.862`, GVR ~`0.018`, denied ~`0.120`)
- **`big_case_score`**: `0.78`
- **Declared `claims` (`cert-v3`)**:
  - `disposition`: `0.88`
  - `relist-increment`: `0.96`
  - `cvsg-increment`: `0.001`
  - `summary-disposition-route`: `0.02`
  - `dissent-from-denial`: `0.30`
- **Declared `claim_distributions` (`order-writers`)**:
  - `Alito`: `0.020`, `Thomas`: `0.015`, `Gorsuch`: `0.010`, `Kavanaugh`: `0.010`, `Sotomayor`: `0.008`, `Jackson`: `0.005`, `Roberts`: `0.003`, `Barrett`: `0.003`, `Kagan`: `0.002`

---

## 2. Provisioned Baseline and Base-Rate Anchoring

### A. Provisioned Snapshot and Context (`2026-09-21.json` & `context.json`)
The provisioned arrival snapshot (`2026-09-21.json`, `snapshot_provenance: "dated"`, `cut_kind: "date"`, `cutoff: "2026-09-22"`, `mode: "forward"`) records the docketing on September 21, 2026 of No. 26-379, *Kenneth Genalo, in His Official Capacity as Field Office Director, New York City Field Office, U.S. Immigration & Customs Enforcement, et al. v. D. C.*, arising from the United States Court of Appeals for the Second Circuit (No. 26-1396). Counsel of record for the federal petitioners is Solicitor General D. John Sauer.

The snapshot contains a single docket entry dated September 21, 2026 noting that the petition for a writ of certiorari was filed (with response due October 21, 2026) and that pursuant to Supreme Court Rule 34.6 and Paragraph 9 of the Guidelines for the Submission of Documents to the Supreme Court's Electronic Filing System, filings in the case are submitted in paper form only (`paper_only_filings: true` in `context.json`, protecting respondent D.C.'s anonymity). As expected for a paper-only Rule 34.6 docket, `record/documents/` is absent and `same-question.json` carries `petitions: null`; per the prompt contract, this is expected and not a provisioning issue.

### B. Statpack Base-Rate Anchor (`cert_anchor` & `metrics/statpack.md`)
Because this is an arrival-moment cert cell (`moment: arrival`, `distribution_count: 0`, `cvsg_date: null`) with a federal petitioner, `context.json` freezes `band: "federal"` under `salience_version: "sal-v7"` and provides the pre-pooled 10-term `cert_anchor`:
- **`cert_anchor.rate`**: `0.7311320754716981` (**73.1%** across `lookback_terms: 10`).
- In `metrics/statpack.md` ("Segment base rate by salience band (sal-v7)"), pooling the 9 rendered prior Terms strictly preceding OT2026 (OT2017–OT2025) gives 155 grants/GVRs out of 212 resolved federal-band petitions (**73.1%**), with individual prior Terms ranging from 47.6% (OT2018, n=21) and 57.1% (OT2025, n=28) to 86.7% (OT2023, n=30), 89.5% (OT2022, n=19), and 96.3% (OT2019, n=27). Across the overall live/historical slice (`n=219` resolved in `federal`), the breakdown is `granted 52.5%, denied 23.3%, gvr 21.0%, dismissed 3.2%` (a 73.5% grant-family rate, or 75.9% among non-dismissed resolutions).
- In the "Modern cert petitions by originating circuit" cut, Second Circuit petitions (`ca2`, `n=2083` resolved) have an overall grant-family rate of 5.0% (`granted 2.6%, gvr 2.4%`), slightly above the all-circuit average.

---

## 3. Case-Specific Evidence: The Direct Replacement Vehicle for *Genalo v. Black* (No. 25-886)

### A. Why *Genalo v. D. C.* Sits Well Above the 73.1% Federal Baseline
In `forward` mode, retrieval from the corpus (`corpus/corpus.db`) and CourtListener RECAP reveals the decisive context behind this petition:
1. **Prior Grant on the Exact Same Questions in *Genalo v. Black* (No. 25-886):** On January 28, 2026, the Solicitor General filed a certiorari petition in *Kenneth Genalo, et al. v. Carol Williams Black, et al.*, No. 25-886 (`scotus/73280386`), seeking review of the Second Circuit's published decision in *Black v. Decker*, 103 F.4th 133 (2d Cir. 2024). In *Black*, the Second Circuit held that (1) mandatory detention of criminal noncitizens pending removal proceedings under 8 U.S.C. § 1226(c) becomes unconstitutional when "unreasonably prolonged" under the three-factor balancing test of *Mathews v. Eldridge*, 424 U.S. 319 (1976), requiring an individualized bond hearing, and (2) at such a bond hearing, the Fifth Amendment Due Process Clause requires the government to justify continued detention by clear and convincing evidence. On **June 15, 2026**, the Supreme Court **granted certiorari** in *Genalo v. Black*.
2. **Mootness Dismissal of *Black* and Explicit Promise of a Replacement Vehicle:** The government filed its opening merits brief in *Genalo v. Black* on August 31, 2026, supported by a 27-State amicus brief led by Iowa Solicitor General Eric Harris Wessan. Shortly thereafter, respondent Black received a gubernatorial pardon of his underlying state convictions, mooting his custody dispute (the companion respondent in *Black v. Decker*, Keisy G.M., had already been removed). On **September 11, 2026**, the Solicitor General filed a letter and Rule 46.1 joint stipulation to dismiss *Black* (`merits_terminated: "voluntary-dismissal"`), expressly advising the Court that the government did so "with the aim of identifying alternative vehicles . . . that would still allow this Court to resolve the questions presented during October Term 2026" (*Rodriguez v. Bondi*, 9th Cir. No. 20-55770, Dkt. 86 & 87, `recap_document_ids: 498346281, 499993913`).
3. **Filing of *Genalo v. D. C.* Ten Days Later:** On **September 21, 2026**, the Solicitor General filed *Genalo v. D. C.*, No. 26-379, presenting the **exact same two questions** that the Court had already agreed to review in *Genalo v. Black* (*Jaimes v. King*, 6th Cir. Nos. 26-1283/26-1821, Dkt. 11, `recap_document_id: 500364921`; *Peters v. Raycraft*, 6th Cir. No. 26-1562, Dkt. 8 & 9, `recap_document_ids: 497682219, 498533601`). Iowa and allied States (`Eric Harris Wessan`) have also filed an amicus brief supporting petitioners on the No. 26-379 docket (`scotus/9026000379`).
4. **Underlying District Court Order (*D.C. v. Noem*, S.D.N.Y. Mar. 20, 2026):** In the underlying habeas proceeding (*C. v. Noem*, No. 1:26-cv-01833-PAE, `docket_id: 72370811`, `recap_document_id: 473020076`), Judge Paul A. Engelmayer directly applied *Black v. Decker*, 103 F.4th 133 (2d Cir. 2024), to hold that respondent D.C.'s ~6.5-month mandatory detention under 8 U.S.C. § 1226(c)(1)(B) at the Orange County Correctional Facility without a bond hearing violated due process, and ordered an Immigration Judge bond hearing by March 27, 2026 at which the government bore the burden of proof by clear and convincing evidence and the IJ had to consider alternatives to detention and ability to pay. Following that hearing, D.C. was released on bond on March 31, 2026 while his cancellation-of-removal application remains pending before the IJ. As in *Black v. Decker*, 103 F.4th at 141–42, D.C.'s release on bond pursuant to the challenged habeas order does not moot the case because reversal of the habeas order would restore mandatory detention under § 1226(c).

### B. Residual Vehicle and Procedural Risks (`denied: 0.12`)
Why do I place `probability` at **0.88** rather than >0.95? Three real counterweights require a ~12% discount:
1. **Certiorari Before Judgment Posture in the Second Circuit:** Because *Black v. Decker* is binding circuit precedent at the panel stage, the government moved on September 2, 2026 for summary affirmance in its Second Circuit appeal (*C. v. Noem*, No. 26-1396, `docket_id: 73412762`), and after D.C. responded by letter on September 17 and 21, 2026, filed this petition for certiorari before judgment on September 21, 2026. Even though Second Circuit law is settled by *Black* (and even if the Second Circuit enters summary affirmance while the cert petition is pending, as it did on September 25, 2026 in *Jules v. Rhoney*, No. 26-1559), respondent D.C. can argue that a district court order pending on appeal—without a published appellate opinion examining D.C.'s specific record—is an inferior vehicle under Supreme Court Rule 11.
2. **Detention Duration (~6.5 Months):** D.C. had been detained for approximately 6.5 months when Judge Engelmayer granted habeas relief, only slightly beyond the six-month benchmark discussed in *Demore v. Kim*, 538 U.S. 510, 530–31 (2003). While respondent Black in *Black v. Decker* was similarly detained for 7 months (and the government views the 6.5-month ruling as proof that *Black* effectively nullifies *Demore* in the Second Circuit), D.C. can argue that the district court's ruling turned on case-specific hearing adjournments between September 2025 and January 2026.
3. **Ongoing Immigration Court Proceedings and Mootness Risk:** D.C.'s application for cancellation of removal remains pending before the Immigration Judge. If the IJ grants cancellation of removal or enters a final removal order (shifting custody authority from 8 U.S.C. § 1226(c) to 8 U.S.C. § 1231) before the Supreme Court acts on the petition, the case could become moot or be perceived as carrying too high a mootness hazard.

---

## 4. Rationale for Secondary Claims and Big Case Score

- **`relist-increment: 0.96`**: From `distribution_count: 0` at arrival, any conference distribution increments the count. Only a pre-distribution Rule 46 dismissal (~4% risk if D.C.'s removal case finishes immediately) would prevent at least one distribution.
- **`cvsg-increment: 0.001`**: The Solicitor General is counsel for petitioners; a CVSG is practically impossible.
- **`summary-disposition-route: 0.02`**: Conditional on a grant, the Court is ~98% likely to set the case for plenary briefing and oral argument (as it did in *Genalo v. Black*) and only ~2% likely to dispose of it in the cert order via GVR or summary reversal.
- **`dissent-from-denial: 0.30` and `order-writers`**: If the Court denies certiorari over vehicle or cert-before-judgment objections, there is a ~30% conditional probability that Justice Alito or Justice Thomas (or Justice Gorsuch/Kavanaugh) writes a dissent from denial or statement respecting denial pointing out that the Court already granted these exact questions in *Black*. Multiplying by the 12% denial probability yields low unconditional per-Justice writing probabilities (`Alito: 0.020`, `Thomas: 0.015`, `Gorsuch: 0.010`, `Kavanaugh: 0.010`, `Sotomayor: 0.008`, `Jackson: 0.005`, `Roberts: 0.003`, `Barrett: 0.003`, `Kagan: 0.002`).
- **`big_case_score: 0.78`**: If decided on the merits, this case resolves the major constitutional question left open in *Jennings v. Rodriguez*, 583 U.S. 281 (2018), governing whether thousands of noncitizens subject to mandatory detention under 8 U.S.C. § 1226(c) nationwide have a Fifth Amendment Due Process right to individualized bond hearings—a high-stakes constitutional and immigration-enforcement issue that already drew 14 amicus briefs (including 27 States on one side and 20 States plus D.C. on the other) in *Genalo v. Black*.
