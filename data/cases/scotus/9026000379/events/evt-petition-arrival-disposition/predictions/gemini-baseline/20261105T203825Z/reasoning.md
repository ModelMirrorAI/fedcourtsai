# Prediction Reasoning — *Kenneth Genalo, et al. v. D. C.* (No. 26-379)

- **Case ID:** `scotus/9026000379`
- **Event ID:** `evt-petition-arrival-disposition` (`stage: cert`, `moment: arrival`)
- **Predictor / Run:** `gemini-baseline` / `20261105T203825Z` (`gemini-4-argon`)
- **Predicted Disposition:** `granted` (`granted: 1`, `probability: 0.78`)
- **Claims:** `disposition: 0.78`, `relist-increment: 0.94`, `cvsg-increment: 0.01`, `summary-disposition-route: 0.04`, `dissent-from-denial: 0.35`
- **Big Case Score:** `0.72`

---

## 1. Anchor & Statpack Base-Rate Calibration

Per `record/context.json`, this cell is at `moment: arrival` in `forward` mode (`snapshot_date: "2026-09-21"`, `cutoff: "2026-09-22"`, `cut_kind: "date"`), with `band: "federal"` (`salience_version: "sal-v7"`), `distribution_count: 0`, `cvsg_date: null`, and `amicus_briefs: null`.

- **Provisioned `cert_anchor.rate`:** `0.731132` (**73.1%**, `lookback_terms: 10`), matching the pooled `federal` band `reached` rate across OT2017–OT2025 in `metrics/statpack.md` ("Segment base rate by salience band (sal-v7)": 2025 57.1% n=28; 2024 62.5% n=16; 2023 86.7% n=30; 2022 89.5% n=19; 2021 75.0% n=12; 2020 67.4% n=43; 2019 96.3% n=27; 2018 47.6% n=21; 2017 75.0% n=16; overall `federal` salience band in `statpack.md` shows n=219 resolved with 52.5% granted, 21.0% GVR, 23.3% denied, 3.2% dismissed).
- **Other Statpack Cuts:**
  - *Originating circuit (`ca2`):* Across modern discretionary-cert petitions (`statpack.md`), `ca2` has `n=2083` resolved cases (denied 92.6%, granted 2.6%, dismissed 2.4%, gvr 2.4%).
  - *Relist count, CVSG status, and amicus-brief count (paid scored segment):* At `moment: arrival`, `distribution_count` is `0`, `cvsg_date` is `null`, and `amicus_briefs` is `null` (an `(unknown)` bucket on a newly docketed petition, which the prompt notes is a timing/polling state rather than absence of future amicus support). As the prompt instructs, on an `arrival` cell we anchor on our caption class's floor (`federal` reached rate = **73.1%**), never on the terminal `relist_bucket = 0` rate (1.8% grant+GVR over `n=10204`), which reflects petitions that *ended* undistributed or un-relisted.
- **Paper-only filings (`paper_only_filings: true`):** The snapshot `2026-09-21.json` carries the Court's Rule 34.6 / Paragraph 9 paper-only filing notice, so `record/documents/` is absent by design and `record/same-question.json` has `petitions: null`.

Starting from the **73.1%** `cert_anchor.rate`, the case-specific record justifies an upward adjustment to **0.78** (`granted: 1`, `predicted_disposition: "granted"`), composed of ~0.75 plenary grant and ~0.03 summary disposition/GVR, against ~0.18 denial and ~0.04 Rule 46 dismissal.

---

## 2. Case-Specific Signals from the Lower-Court Record & Predecessor Docket

### A. Direct Replacement Vehicle for *Genalo v. Black* (No. 25-886)

Corpus query (`uv run fedcourts query --court scotus --docket-number 25-886`) and CourtListener retrieval establish that this petition is the Solicitor General's immediate replacement vehicle for *Kenneth Genalo, Director of the New York Field Office of U.S. Immigration and Customs Enforcement, et al. v. Carol Williams Black, et al.*, No. 25-886 (`scotus/73280386`):

1. In *Black v. Decker*, 103 F.4th 133 (2d Cir. 2024), the Second Circuit held that:
   - The Fifth Amendment's Due Process Clause prohibits "unreasonably prolonged" mandatory detention under 8 U.S.C. § 1226(c) without an individualized bond hearing, evaluated under the three-factor balancing test of *Mathews v. Eldridge*, 424 U.S. 319 (1976); and
   - At such a bond hearing, due process requires placing the burden on the government to justify continued detention by clear and convincing evidence, and requires the Immigration Judge (IJ) to consider alternatives to detention and the noncitizen's ability to pay.
2. On October 24, 2025, the Second Circuit denied rehearing en banc over a five-judge dissent (*Black v. Almodovar; G.M. v. Almodovar*, 156 F.4th 171 (2d Cir. 2025), `opinion_id: 11176990`). Judge Nardini (joined by Chief Judge Livingston and Judges Sullivan, Park, and Menashi) detailed the deep multi-circuit split on both questions—contrasting the Second and Third Circuits (*Black*, 103 F.4th 133; *German Santos v. Warden Pike County Correctional Facility*, 965 F.3d 203 (3d Cir. 2020)) with the Eighth Circuit (*Banyee v. Garland*, 115 F.4th 928 (8th Cir. 2024)) and the Fourth and Ninth Circuits (*Miranda v. Garland*, 34 F.4th 338 (4th Cir. 2022); *Rodriguez Diaz v. Garland*, 53 F.4th 1189 (9th Cir. 2022))—and wrote that "only the Supreme Court can clean up this intercircuit incoherence."
3. **On June 15, 2026, the Supreme Court granted certiorari in *Genalo v. Black* (No. 25-886).** The Solicitor General filed the opening merits brief on August 31, 2026, and oral argument was set for October 13, 2026.
4. On August 28, 2026, New York Governor Kathy Hochul pardoned respondent Keisy G.M. for the drug conviction underlying his § 1226(c) detention (and the other respondent, Carol Williams Black, had already left the country). On **September 11, 2026**, the Supreme Court dismissed *Genalo v. Black* as moot under Rule 46.1 (`merits_terminated: "voluntary-dismissal"`), leaving *Black v. Decker* intact as binding Second Circuit precedent.
5. Ten days later, on **September 21, 2026**, the Solicitor General filed the present petition in *Genalo v. D.C.* (No. 26-379), presenting the **exact same two Questions Presented** that the Court had already granted in No. 25-886.

### B. District Court and Second Circuit Record in *D.C. v. Noem* (`1:26-cv-01833` / `26-1396`)

Using the CourtListener MCP server, I retrieved and read the full 29-page S.D.N.Y. Opinion & Order in *D.C. v. Noem*, 825 F. Supp. 3d 309 (S.D.N.Y. Mar. 20, 2026) (`recap_document_id: 473020076`), and the Second Circuit docket in *C. v. Noem*, No. 26-1396 (`docket_id: 73412762`):

- Respondent D.C., a 62-year-old Dominican citizen with prior New York convictions (including a 1998 controlled-substance conviction), was detained by ICE under § 1226(c) on September 8, 2025. In February 2026, an IJ found D.C. mentally incompetent (due to persecutory delusional disorder and neurocognitive impairment exacerbated by untreated diabetes and hypertension) but allowed removal proceedings to proceed with safeguards.
- On March 20, 2026, after D.C. had been detained for nearly 6.5 months, Judge Paul A. Engelmayer applied *Black v. Decker* and *Mathews v. Eldridge* to grant D.C.'s habeas petition in part, ordering an individualized bond hearing before an IJ at which (1) the government bore the burden of proof by clear and convincing evidence that D.C. posed a flight risk or danger to the public, (2) the IJ had to consider alternatives to detention for both flight risk and dangerousness, and (3) the IJ had to consider ability to pay.
- Following the March 26, 2026 bond hearing, D.C. posted bond and was released on March 31, 2026.
- The government appealed to the Second Circuit (`No. 26-1396`, filed May 20, 2026) and on September 2, 2026 moved for summary affirmance (Entry 17) because *Black v. Decker* is binding circuit precedent. On September 17, 2026 (Entry 18), D.C. responded that he did not oppose summary affirmance. On September 21, 2026, while the Second Circuit's formal order on the unopposed summary-affirmance motion remained pending, the Solicitor General filed this petition for certiorari before judgment under Rule 11.

---

## 3. Rationale for Adjustments & Secondary Claims

1. **Upward adjustment from 0.731 to 0.78 (`disposition: 0.78`):**
   - The Court's June 15, 2026 grant of certiorari in *Genalo v. Black* (No. 25-886) on the identical Questions Presented from the Second Circuit proves that at least four Justices already view the constitutional validity of *Black v. Decker* under 8 U.S.C. § 1226(c) as warranting plenary review.
   - However, two factors restrain the probability from climbing into the 85–90% range:
     - **Rule 11 posture and pending Second Circuit summary affirmance:** Although summary affirmance is unopposed in `26-1396`, the petition was filed before the Second Circuit entered judgment. Even if the Second Circuit enters summary affirmance before the Court's conference (which will cure the Rule 11 objection), Respondent D.C. has obtained an extension until December 8, 2026 to file his brief in opposition.
     - **Case-specific vehicle and mootness risks:** D.C. will argue in opposition that his mental incompetency adjudication, acute medical deterioration at Orange County Jail, and Judge Engelmayer's additional dangerousness-alternatives requirement make this case an atypical vehicle. Additionally, there is an ongoing ~4% hazard that D.C.'s underlying removal proceedings terminate before cert disposition, mooting the habeas dispute as occurred in *Genalo v. Black*. (By contrast, D.C.'s release on bond pursuant to the habeas order does not moot the case, just as Carol Williams Black's release on bond did not moot *Black v. Decker*.)
2. **Secondary Claims:**
   - `relist-increment: 0.94` — Because the arrival snapshot has `distribution_count: 0`, any conference distribution increments the count above the frozen baseline (`0 -> >=1`). Only a pre-distribution Rule 46 dismissal or withdrawal (~6% combined risk) would prevent at least one distribution.
   - `cvsg-increment: 0.01` — The Solicitor General is counsel of record for Petitioners; the Court does not invite the SG's views when the United States is the petitioner.
   - `summary-disposition-route: 0.04` — Conditional on a grant, plenary review (~96% of grants here) is vastly likelier than a summary reversal or GVR (~4% of grants), because the Court already granted plenary review on these exact questions in *Genalo v. Black* and there is no intervening Supreme Court decision on § 1226(c) to support a GVR.
   - `dissent-from-denial: 0.35` and `order-writers` — Conditional on a denial (e.g., on vehicle or Rule 11 grounds), there is roughly a 35% chance that a conservative Justice (most likely Justice Thomas or Justice Alito, at 0.04 unconditional each) writes a dissent or statement respecting denial highlighting the need to resolve the *Black v. Decker* split in a future vehicle.
   - `big_case_score: 0.72` — High doctrinal and operational significance: resolves a deep multi-circuit split on Fifth Amendment due process limits on mandatory immigration detention under 8 U.S.C. § 1226(c), affecting thousands of removal proceedings nationwide.
