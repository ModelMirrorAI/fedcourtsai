# Certiorari Prediction Reasoning: *Fiona Havlish, et al. v. The Taliban, et al.* (No. 26-292)

## 1. Executive Summary & Calibrated Forecast

- **Predicted Disposition:** `denied` (`granted: 0`)
- **Probability of Certiorari Grant (`probability` / `disposition`):** `0.22`
- **Relist-Increment Probability (`relist-increment`):** `0.38`
- **CVSG-Increment Probability (`cvsg-increment`):** `0.18`
- **Summary-Disposition Route Conditional on Grant (`summary-disposition-route`):** `0.08`
- **Dissent or Statement Conditional on Denial (`dissent-from-denial`):** `0.16`
- **Big-Case Score (`big_case_score`):** `0.82`

We predict that the Supreme Court will ultimately **deny** the petition for a writ of certiorari (`probability = 0.22`), though there is a substantial likelihood (`0.38`) of at least one further distribution beyond the November 13, 2026 Conference—either to accommodate a Call for the Views of the Solicitor General (`cvsg-increment = 0.18`), additional conference deliberation across the three Vide dockets (`26-292`, `26-293`, and `26-294`), or a separate statement/dissent respecting the denial of certiorari (`dissent-from-denial = 0.16`).

---

## 2. Baseline Anchor & Procedural Posture

From `record/context.json` and `metrics/statpack.md`, this prediction is evaluated at the `distribution` moment for a `cert`-stage petition assigned to the **`elevated` salience band**:

- **10-Term Pooled Elevated-Band Base Rate (`cert_anchor.rate`):** `0.2481` (24.8%, pooled across OT 2016–OT 2025; OT 2025 elevated-band rate was `0.333`, 33.3%).
- **Statpack Signal Cuts (`metrics/statpack.md`, paid scored segment):**
  - By relist count: `1` relist (`distribution_count = 2` on the docket) carries a 21.8% grant rate (`granted` 20.9% + `gvr` 0.9%, `n = 110`); `2` relists carries 31.1% (`n = 45`).
  - By CVSG status: `no CVSG` carries a 13.7% grant rate (`granted` 12.1% + `gvr` 1.6%, `n = 439`), whereas `CVSG` carries 44.0% (`n = 25`).
  - By amicus-brief count: `2+` amicus briefs carries a 38.9% grant rate (`n = 72`, with `unknown = 278` noted as a coverage gap). Here, `2026-11-09.json` records 2 amicus briefs filed on October 5, 2026 (one by Iowa, et al. supporting Petitioners, and one VIDED brief by Chargé d'Affaires Naseer A. Faiq opposing turnover).
- **Snapshot Docket & Related Vide Dockets (`2026-11-09.json`, `record/related/26-293.json`, `record/related/26-294.json`):**
  - On June 18, 2026, Justice Sotomayor granted a 60-day extension to file (`25A1393`).
  - On August 31, 2026, Petitioners (the *Havlish*, *Doe*, *Federal Insurance*, and *Smith* 9/11 judgment creditors) filed their petition for a writ of certiorari (`26-292`), docketed September 4, 2026, as part of a coordinated three-petition `Vide` package (`record/related/related.json`, `relation: "Vide"`) alongside No. `26-293` (*Kathleen Ashton, et al. v. The Taliban, et al.*) and No. `26-294` (*James Owens, et al. v. The Taliban, et al.*). `record/same-question.json` reports no other pending petitions matching above the similarity threshold (`petitions: []`).
  - Neither Respondent—the Taliban nor Da Afghanistan Bank (DAB)—has ever appeared in the litigation below or in this Court (`response_filed_at: null`, `response_requested: false`).
  - After an initial October 7 distribution for the October 16 Conference was rescheduled on October 9 to align the three Vide petitions, `26-292`, `26-293`, and `26-294` were distributed on October 21, 2026 for the November 6, 2026 Conference.
  - On October 30, 2026—one week before the November 6 Conference—Petitioners filed a motion for leave to file a supplemental brief (`Distributed`). (That supplemental brief and the two October 5 amicus briefs were not staged in `record/documents/`, so we rely on `questions-presented.txt`, `petition.txt`, `appendix.txt`, the snapshot docket, and the full Second Circuit opinions retrieved via CourtListener MCP.)
  - On Monday, November 9, 2026, while routine November 6 Conference petitions were denied on the order list, all three Vide petitions (`26-292`, `26-293`, and `26-294`) were **relisted** (`DISTRIBUTED for Conference of 11/13/2026`, `distribution_count = 2`).

---

## 3. Case-Specific Signals Pushing Toward vs. Against Certiorari

### A. Factors Supporting Certiorari (`+` Adjustments)

1. **First Relist Across All Three Vide Petitions & Elite Supreme Court Bar Representation:**
   Under modern Supreme Court practice, a relist after the first conference (`distribution_count = 2`) is a necessary milestone for almost every paid grant and moves the petition into the `elevated` salience band (`0.2481`). Petitioners across the three Vide petitions are represented by experienced Supreme Court counsel—Lee Wolosky (Jenner & Block), Stuart H. Singer (Boies Schiller Flexner), and Sean P. Carter (Cozen O'Connor) in `26-292`; Samuel Issacharoff in `26-293`; and Matthew D. McGill (Gibson Dunn) in `26-294`—backed by a state amicus coalition led by Iowa.
2. **Vigorous Appellate Division Below (2–1 Panel Split and 5-Judge En Banc Dissent):**
   In *Havlish v. The Taliban*, 152 F.4th 339 (2d Cir. 2025), Judges Cabranes and Calabresi affirmed the denial of turnover of $3.5 billion in blocked DAB funds held at the Federal Reserve Bank of New York (FRBNY) over a forceful dissent by Judge Sullivan. When the Second Circuit denied rehearing en banc, 170 F.4th 100 (2d Cir. 2026), **five active judges** dissented in two detailed opinions—Judge Sullivan (joined by Chief Judge Livingston and Judges Bianco and Park) and Judge Menashi—specifically criticizing the panel majority's sua sponte holding that an entity's status as an "agency or instrumentality of that terrorist party" under Section 201(a) of the Terrorism Risk Insurance Act of 2002 (TRIA), Pub. L. No. 107-297, 116 Stat. 2322, 2337 (28 U.S.C. § 1610 note), must be assessed as of the date the assets were blocked (August 15, 2021) rather than when turnover is sought.
3. **Pure Statutory Textual Argument Under TRIA § 201(a):**
   As Judges Sullivan and Menashi emphasized in dissent, TRIA § 201(a) authorizes execution against "the blocked assets of that terrorist party (including the blocked assets of any agency or instrumentality of that terrorist party)" without any textual requirement that the agency-or-instrumentality relationship have existed on the date of the initial blocking order.

### B. Factors Weighing Against Certiorari (`-` Adjustments)

1. **Formidable Vehicle, Ownership, and Article II Constitutional Obstacles:**
   As Judge Nardini explained in his concurrence in the denial of rehearing en banc (170 F.4th at 101–04), reversing the panel's TRIA blocking-date timing rule would not resolve whether Petitioners can execute on DAB's $3.5 billion central-bank reserves:
   - **Statutory Ownership ("of") Requirement:** TRIA § 201(a) authorizes execution only on blocked assets "**of** that terrorist party (including the blocked assets **of** any agency or instrumentality of that terrorist party)." Settled precedent holds that this requires actual property ownership (*Hausler v. JP Morgan Chase Bank, N.A.*, 770 F.3d 207, 212 (2d Cir. 2014); *Heiser v. Islamic Republic of Iran*, 735 F.3d 934, 940 (D.C. Cir. 2013); *Bank Markazi v. Peterson*, 578 U.S. 212, 217 n.2 (2016)). Even if the Taliban physically captured DAB's Kabul offices in August 2021, the $3.5 billion in sovereign central-bank reserves at the FRBNY are owned by the recognized State of Afghanistan, not by the unrecognized Taliban regime.
   - **Article II Recognition Barrier Avoided Below:** In the district court, Judge Daniels held that the Judiciary is **constitutionally barred** under *Zivotofsky v. Kerry*, 576 U.S. 1 (2015), from treating the Taliban as in control of the central bank of Afghanistan because doing so would conflict with the President's exclusive recognition power (*In re Terrorist Attacks on September 11, 2001*, 657 F. Supp. 3d 311, 333–36 (S.D.N.Y. 2023)). The Second Circuit panel explicitly invoked the canon of constitutional avoidance in footnote 124 (152 F.4th at 362 n.124) to avoid deciding that constitutional question. Thus, `26-292` cannot cleanly deliver relief without confronting the very Article II recognition and FSIA foreign-state issues presented in `26-293` and `26-294`.
2. **Absence of a Genuine, Square Circuit Split:**
   Petitioners' claimed conflict with *Stansell v. Revolutionary Armed Forces of Colombia*, 45 F.4th 1340, 1350 (11th Cir. 2022), and *Bennett v. Islamic Republic of Iran*, 825 F.3d 949, 963 (9th Cir. 2016), is asymmetric. In *Stansell*, OFAC blocked the assets *because* the owners were FARC agencies or instrumentalities when blocked, and the Eleventh Circuit held that a subsequent lapse in terrorist-instrumentality status could defeat turnover at the time of execution. In *Bennett*, Bank Melli was a wholly owned instrumentality of Iran (the terrorist party) at all relevant times. No court of appeals has ever addressed—much less permitted TRIA attachment in—the sui generis situation where the President freezes the central-bank reserves of a recognized, non-terrorist foreign sovereign *to protect them from an invading terrorist group*.
3. **Executive Branch Foreign-Policy Interests & Adversarial Deficit:**
   The United States participated via Statements of Interest in the district court and as amicus curiae in the Second Circuit opposing attachment and turnover of DAB's reserves, and the Executive Branch transferred $3.5 billion of the blocked reserves into the Swiss-based "Fund for the People of Afghanistan" (the Afghan Fund). The Supreme Court is historically reluctant to grant certiorari to overturn a circuit judgment that protects foreign central-bank reserves in alignment with the Executive Branch's foreign-policy position—particularly where no respondent has appeared to defend the judgment below (`response_filed_at: null`).
4. **Late Supplemental Brief Explains the November 9 Relist:**
   Petitioners filed a motion for leave to file a supplemental brief on Friday, October 30, 2026—just one week before the November 6 Conference. A one-week relist on November 9 to the November 13 Conference is standard procedure when a supplemental brief is distributed shortly before conference in a complex multi-docket Vide cluster.

---

## 4. Quantitative Calibration Summary

Starting from the elevated-band base rate (`0.2481`, closely aligned with the 1-relist paid-segment rate of `0.218`):
- **Upward adjustments (`+0.09`):** Five-judge Second Circuit en banc dissent on an important statutory TRIA question (`+0.05`), $3.5 billion stakes in 9/11 judgment enforcement (`+0.02`), and coordinated three-petition Vide representation by top Supreme Court advocates supported by a multi-state amicus brief (`+0.02`).
- **Downward adjustments (`-0.12`):** Complete absence of a respondent or brief in opposition (`-0.04`), October 30 late supplemental brief explaining the initial relist without requiring a grant inclination (`-0.02`), severe alternative-ground / ownership / Article II recognition obstacles highlighted by Judge Nardini and the district court (`-0.03`), and Executive Branch opposition to turnover coupled with the absence of a square circuit split on post-blocking capture of foreign central-bank reserves (`-0.03`).
- **Net Forecast:** `0.2481 + 0.09 - 0.12 ≈ 0.22` (`granted: 0`, `predicted_disposition: "denied"`).
- **Ancillary Claims & Order-Writers Distribution:**
  - `relist-increment = 0.38`: 38% probability of at least one additional distribution beyond the November 13, 2026 Conference.
  - `cvsg-increment = 0.18`: 18% probability that the Court invites the Solicitor General's views before disposing of the petition.
  - `summary-disposition-route = 0.08`: Conditional on a grant, 8% probability of summary disposition (e.g., GVR) vs. 92% plenary review.
  - `dissent-from-denial = 0.16` and `order-writers`: Conditional on a denial, 16% probability that at least one Justice writes a dissent from or statement respecting the denial of certiorari, concentrated in Justices Gorsuch (`0.05`), Thomas (`0.045`), and Alito (`0.045`).
