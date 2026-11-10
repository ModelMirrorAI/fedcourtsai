# Certiorari Prediction Rationale: *Raul Rivera-Perez v. Caryn Flowers, Warden*, No. 26-396

## I. Summary of Numbers

- **Predicted Disposition:** `denied` (`granted = 0`)
- **`probability` (`disposition` claim):** `0.01` (`1.0%`)
- **`big_case_score`:** `0.25` — A recurring statutory interpretation question under the First Step Act of 2018 (18 U.S.C. § 3632(d)(4)(C)) affecting the administration of federal supervised release terms, with uniform circuit precedent and moderate practical stakes for federal prisoners.
- **Declared Claims (`cert-v3`):**
  - `disposition`: `0.01`
  - `relist-increment`: `0.03`
  - `cvsg-increment`: `0.001`
  - `summary-disposition-route`: `0.15` (conditional on a grant)
  - `dissent-from-denial`: `0.02` (conditional on a denial)
- **Declared Distribution Claims:**
  - `order-writers`: `Roberts: 0.001`, `Thomas: 0.002`, `Alito: 0.001`, `Sotomayor: 0.010`, `Kagan: 0.002`, `Gorsuch: 0.005`, `Kavanaugh: 0.001`, `Barrett: 0.001`, `Jackson: 0.008`

---

## II. Base Rate Anchor and Statpack Cuts

1. **Salience Band Anchor (`band: "baseline"`, `sal-v8`):**
   - `record/context.json` freezes `band: "baseline"`, `distribution_count: 1`, `cvsg_date: null`, `amicus_briefs: null`, `term: 2026`, and `cert_anchor.rate: 0.051588` (5.16%, 10-Term lookback).
   - In `metrics/statpack.md` (*Segment base rate by salience band (sal-v8)*), the `baseline` band's bracketed `reached` grant rate across the 10 preceding Terms (OT2017–OT2025) sits between **4.0%** (OT2025, `n=1290`) and **6.0%** (OT2023 `n=1283`, OT2024 `n=1243`), while the terminal `baseline` grant rate (petitions that never escalate out of `baseline` via a Call for a Response, relist, or CVSG) is **0.6% to 1.9%** (1.3% in OT2025, `n=1116`; pooled `baseline` cut in `statpack.md`: denied 97.3%, dismissed 1.3%, granted 0.8%, gvr 0.6% over `n=11020` resolved).
2. **Relist, CVSG, and Amicus Cuts (Paid Scored Segment):**
   - **Relist count (`0` relists so far, `distribution_count = 1`):** In `statpack.md` (*Cert petitions by relist count (paid scored segment)*), petitions resolving at `0` relists (`n=10204` resolved) are `denied 96.8%, dismissed 1.3%, granted 1.3%, gvr 0.5%` (1.8% grant-family rate).
   - **CVSG status (`none`):** Petitions without a CVSG (`n=13550` resolved) are `denied 92.4%, granted 4.1%, gvr 2.3%, dismissed 1.2%`. Here a CVSG is functionally ruled out because the United States (through the federal warden respondent represented by the Solicitor General) is already a party.
   - **Amicus count (`0` cert-stage amici on the snapshot):** Petitions with `0` cert-stage amicus briefs (`n=11109` resolved) have a grant-family rate of **3.8%** (`denied 95.0%, granted 2.0%, gvr 1.8%, dismissed 1.3%`).

---

## III. Case-Specific Adjustments from the Anchor

Starting from the `cert_anchor` of **5.16%** (`baseline` reached rate), several strong case-specific signals push the grant probability down to **1.0%** (`0.01`):

### 1. Waiver of Response and Distribution Without a Call for a Response (Strong Downward Adjustment)
The provisioned snapshot (`2026-11-09.json`) shows that the petition was docketed on September 22, 2026, the Solicitor General filed a waiver of the right of respondent Caryn Flowers to respond on October 21, 2026, and the petition was distributed on November 4, 2026, for the Conference of November 20, 2026 (`distribution_count: 1`), with no Call for a Response (`response_requested` is absent). Because the Court almost never grants plenary review without first calling for a response, the petition would first have to attract a CFR from a Justice's chambers, survive the brief in opposition, and then be granted. That hurdle already eliminates the vast majority of the 5.16% risk-set rate.

### 2. Unbroken `0–8` Circuit Consensus Against Petitioner (Strong Downward Adjustment)
As both the Second Circuit majority opinion (Pet. App. 20a & n.11) and the petition itself (Pet. 3, 28) recognize, **eight Courts of Appeals** have decided whether First Step Act time credits under 18 U.S.C. § 3632(d)(4)(C) can be applied to reduce the length of a post-imprisonment term of supervised release, and **all eight** have held that they cannot:
- **Second Circuit:** *Rivera-Perez v. Stover*, 171 F.4th 105 (2d Cir. 2026) (decision below)
- **Third Circuit:** *DOJ v. Hudson*, No. 24-2646, 2025 WL 2058826 (3d Cir. July 23, 2025)
- **Fourth Circuit:** *Valladares v. Ray*, 130 F.4th 74, 79–84 (4th Cir. 2025)
- **Fifth Circuit:** *United States v. Hanner*, 32 F.4th 430, 433–34 (5th Cir. 2022)
- **Sixth Circuit:** *Hargrove v. Healy*, 154 F.4th 356, 360–71 (6th Cir. 2025)
- **Seventh Circuit:** *Mancillas v. Federal Bureau of Prisons*, 163 F.4th 459 (7th Cir. 2025)
- **Ninth Circuit:** *Gonzalez v. Herrera*, 151 F.4th 1076, 1080–87 (9th Cir. 2025)
- **Eleventh Circuit:** *Guerriero v. Miami RRM*, No. 24-10337, 2024 WL 2017730 (11th Cir. May 7, 2024)

CourtListener retrieval confirms that no court of appeals has broken ranks since the Second Circuit's March 26, 2026 decision. While petitioner emphasizes Judge Calabresi's dissent below and earlier district court decisions (now superseded in their respective circuits), an intra-panel dissent against an 8–0 circuit consensus does not satisfy Supreme Court Rule 10.

### 3. Recent Denial of Certiorari on the Identical Question in *Hargrove v. Healy*, No. 25-818 (Strong Downward Adjustment)
Corpus lookup (`fedcourts query --court scotus --docket-number 25-818 --include-open --full`) confirms that on **April 20, 2026**, the Supreme Court denied certiorari in *Terrell Anthony Hargrove v. Ian Healy, Warden*, No. 25-818 (originating from the Sixth Circuit's published decision in *Hargrove v. Healy*, 154 F.4th 356). *Hargrove* presented the identical question under 18 U.S.C. § 3632(d)(4)(C) and was supported by an amicus brief from the Cato Institute, NACDL, the Rutherford Institute, and the Law Enforcement Action Partnership, yet it was denied at its first conference (`distribution_count: 1`) without a response being requested. Nothing has changed in the circuit landscape since April 2026 except that the Second Circuit joined the unanimous appellate consensus.

### 4. Modest Countervailing Signals (Why `P(grant)` is `0.01` Rather Than `<0.005`)
Two factors prevent the probability from dropping all the way to zero:
- **Experienced Supreme Court Counsel and Published Panel Dissent:** Petitioner is represented by Ashley Robertson of the Federal Public & Community Defenders Supreme Court Project alongside Jeffrey L. Fisher and Pamela S. Karlan of the Stanford Law School Supreme Court Litigation Clinic, and the decision below features a thorough, 17-page published dissent by Judge Calabresi (Pet. App. 27a–45a) arguing that the literal text of § 3632(d)(4)(C) ("shall be applied toward time in prerelease custody or supervised release") permits reducing supervised release.
- **Pending Related Statute Case (*Maxwell v. Dinis*, No. 25-5930):** On June 1, 2026, the Court granted certiorari in *Maxwell v. Dinis*, No. 25-5930, which concerns the second sentence of 18 U.S.C. § 3632(d)(4)(C) (whether the BOP has a mandatory duty to transfer eligible prisoners into prerelease custody). However, in *Maxwell*, the Solicitor General confessed error in part and supported vacatur, whereas here the Government defends the uniform circuit rule and waived its response. Moreover, *Maxwell*'s question (whether "shall transfer" into prerelease custody is mandatory while a prisoner is still serving his prison term) is distinct from whether unused credits can shorten a post-release term of supervised release in the teeth of 18 U.S.C. § 3624(g)(3) and *United States v. Johnson*, 529 U.S. 53 (2000).

---

## IV. Rationale for Secondary Claims and Distributions

- **`relist-increment` (`0.03`):** Because the Solicitor General waived a response, any serious interest by a Justice would first manifest as a Call for a Response (CFR) followed by a second distribution after the BIO is filed (~3% chance given Stanford Clinic representation and Judge Calabresi's dissent).
- **`cvsg-increment` (`0.001`):** The respondent warden is a federal official represented by the Solicitor General (`D. John Sauer`), so the Court does not issue a CVSG when the United States is already a party (`0.001` rounding floor).
- **`summary-disposition-route` (`0.15` conditional on grant):** Conditional on the unlikely event of a grant, plenary review (`0.85`) is much more likely than a summary disposition (`0.15`), because the Court would not summarily reverse an 8–0 circuit consensus, and *Maxwell v. Dinis* addresses prerelease custody rather than supervised release length (leaving only a small ~15% conditional probability of a post-*Maxwell* GVR if *Maxwell*'s statutory analysis of § 3632(d)(4)(C) were written broadly enough to touch the first sentence).
- **`dissent-from-denial` (`0.02`) and `order-writers`:** *Hargrove v. Healy* (No. 25-818) drew no dissent from denial in April 2026. Given Judge Calabresi's textual and purposive dissent below, there is a small (~2%) chance that a Justice—most plausibly Justice Sotomayor (`0.010`), Justice Jackson (`0.008`), or Justice Gorsuch (`0.005`)—authors a brief statement or dissent respecting the denial of certiorari.

---

## V. Provisioned Inputs and Limitations

- **Snapshot:** Read `data/cases/scotus/9026000396/record/snapshots/2026-11-09.json` (`input_snapshot: "2026-11-09.json"`).
- **Provisioned Documents:** Read `petition.txt`, `questions-presented.txt`, `party-letter.txt`, and `documents.json`. Note that Appendix A of `petition.txt` had 4,383 characters omitted at the very end of Judge Calabresi's dissent (PDF pages 90–92) and Appendix B (the District of Connecticut opinion) had 36,679 characters omitted due to the 150,000-character pipeline cap; neither truncation affected the analysis because the full Second Circuit majority opinion and nearly all of Judge Calabresi's dissent were intact in `petition.txt`.
