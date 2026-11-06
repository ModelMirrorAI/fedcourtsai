# Prediction Rationale: *Juan Matthews v. Louisiana*, No. 26-218 (`evt-petition-disposition`)

## I. Summary of Numbers

- **`granted`:** `0`
- **`probability` (`disposition`):** `0.015`
- **`predicted_disposition`:** `"denied"`
- **`big_case_score`:** `0.15`
- **Declared Claims (`cert-v3`):**
  - `disposition`: `0.015`
  - `relist-increment`: `0.08`
  - `cvsg-increment`: `0.001`
  - `summary-disposition-route`: `0.65`
  - `dissent-from-denial`: `0.04`

---

## II. Base-Rate Anchoring (`context.json` and `metrics/statpack.md`)

From `record/context.json`, this cell runs in `forward` mode at `moment: distribution` on snapshot `2026-11-05.json`, with frozen conditioning state:
- **`band`:** `"baseline"` under `salience_version: "sal-v7"`
- **`distribution_count`:** `1`
- **`cvsg_date`:** `null`
- **`term`:** `2026`
- **`cert_anchor.rate`:** `0.051512996760685784` (`~5.15%`, pooled over `lookback_terms: 10`, OT2017–OT2025, for the `baseline` band's bracketed `reached` risk-set grant rate in `metrics/statpack.md`).

Starting from the `5.15%` risk-set `baseline` band anchor, the signal cuts in `metrics/statpack.md` (and the docket's specific posture in `record/snapshots/2026-11-05.json`) point sharply downward:
1. **Amicus Count = 0:** In the paid scored segment, petitions ending with `0` amicus briefs have a `3.8%` grant-family rate (`granted 2.0%, gvr 1.8%, denied 95.0%`, `n=11,109` resolved), compared to `14.8%` with 1 amicus brief (`n=1,158`) and `22.7%` with `2+` (`n=1,446`). No amicus briefs have been filed in support of Matthews.
2. **Relist Count = 0 (`distribution_count == 1`) & Respondent Waiver Without a CFR:** Petitions that resolve without a relist (`relist_bucket = 0`, `n=10,204` resolved) grant at `1.8%` (`granted 1.3%, gvr 0.5%, denied 96.8%`), and petitions ending in the `baseline` band (`n=11,020` resolved) grant at `1.4%` (`granted 0.8%, gvr 0.6%, denied 97.3%`). Moreover, the snapshot shows that Respondent State of Louisiana **waived its right to respond** on October 27, 2026, and the petition was distributed on November 4, 2026 for the November 20, 2026 conference without a call for a response (CFR). Because the Court virtually never grants certiorari, GVRs, or summarily reverses a state criminal judgment on a waiver without first calling for a response and relisting, a grant here requires *first* surviving the low-probability hurdle of a CFR (`relist-increment` estimated at `0.08`) and *then* overcoming severe vehicle and merits obstacles once the State files its brief in opposition.
3. **Same-Question List (`record/same-question.json`):** `petitions: []` (0 matches at or above the `0.5` cosine threshold across `13,523` indexed petitions), and `vide_links: []` (no companion or cross-petitions).

---

## III. Case-Specific Adjustments from Provisioned Filings and Priors

Weighing `record/documents/questions-presented.txt`, `record/documents/petition.txt`, and `record/documents/appendix.txt` alongside priors retrieved via `uv run fedcourts query` and the CourtListener MCP server drives a further downward adjustment from the `5.15%` anchor to **`0.015` (`1.5%`)**:

### 1. The Court Just Denied *Skinner v. Louisiana* (No. 25-1) on the Identical Question Presented
Petitioner's single question presented asks: *"Whether the Louisiana courts erred by denying Petitioner Juan Matthews's Brady claim based on the sufficiency of the evidence at trial."* (QP at i.) As the Petition candidly acknowledges (Pet. 32–33), the Court considered the exact same question last Term in *James Skinner v. Louisiana*, No. 25-1 (`scotus/73110505`). Corpus query results for `25-1` show that *Skinner* had **seven amicus briefs** (Innocence Network, Cato Institute, Patrick O'Neal, Two Louisiana Prisoners, Professors Z. Payvand Ahdout & Lee Kovarsky, Prof. Brandon Garrett, and Law Professors) and was distributed **9 times** (8 relists) before the Court **denied** certiorari on March 30, 2026 without any recorded dissent.

Similarly, in *David Brown v. Louisiana*, No. 22-77 (`scotus/67123792`, 143 S. Ct. 886 (2023)), a capital *Brady* materiality petition from the Louisiana Supreme Court supported by multiple amici, the Court denied certiorari after 7 distributions over a three-Justice dissent by Justice Jackson (joined by Justices Sotomayor and Kagan). And in *Klein v. Martin*, No. 25-51, 607 U.S. ___ (Jan. 26, 2026) (per curiam) (retrieved via CourtListener MCP, `opinion_id: 11246089`), the Court's most recent *Brady* materiality intervention summarily *reversed* the Fourth Circuit for granting habeas relief where the state court had rejected a *Brady* claim in light of strong trial evidence. Where a heavily amicused petition raising the identical question (*Skinner*) failed to attract four votes after 9 conferences in March 2026, an unamicused petition with an explicit state procedural bar is far weaker.

### 2. Independent and Adequate State Procedural Bar on the Face of the Judgment Below
Inspection of Appendix A (`record/documents/appendix.txt`, Pet. App. 1a–2a) reveals a threshold jurisdictional/vehicle barrier that the Petition largely glosses over. Matthews was convicted in October 1992 of second-degree murder, and his conviction became final in 1998. After two unsuccessful pro se post-conviction applications in 2018 and 2019, the Louisiana Supreme Court held in 2019 that Matthews had exhausted his right to state collateral review (*State ex rel. Matthews v. State*, 279 So. 3d 884 (La. 2019), Pet. App. 50a–51a). Although Innocence Project New Orleans (IPNO) obtained the NOPD homicide file via public records request in **2012** (Pet. 10), Matthews waited another **twelve years**—until June 2024—to file this third post-conviction application.

In its May 19, 2026 per curiam order denying supervisory writs (*State v. Matthews*, 423 So. 3d 1219 (La. 2026), Pet. App. 1a–2a), the Louisiana Supreme Court consisted of two sentences:
1. *"Writ denied. Applicant fails to show that the state withheld material exculpatory evidence in violation of Brady v. Maryland, 373 U.S. 83 (1963)."*
2. *"Look also to the fact that applicant has previously exhausted his right to state collateral review, see State ex rel. Matthews v. State, 19-0087 (La. 9/24/19), 279 So. 3d 884, and he fails to show that any exception permits his third application, filed more than thirty years after his conviction and sentence. See La.C.Cr.P. art. 930.4; La.C.Cr.P. art. 930.8."*

Under *Coleman v. Thompson*, 501 U.S. 722, 729 (1991), and *Michigan v. Long*, 463 U.S. 1032 (1983), the Louisiana Supreme Court's explicit invocation of state procedural bars for repetitive and untimely post-conviction applications (`La.C.Cr.P. arts. 930.4 & 930.8`) constitutes an independent and adequate state-law ground that would defeat Supreme Court jurisdiction or immediately prompt a vehicle objection if the State were asked to respond.

### 3. Mismatch Between the Question Presented and the Lower Courts' Actual Reasoning
Even setting aside the state procedural bar, the lower-court rulings reproduced in the Appendix do not support Petitioner's contention that the Louisiana courts applied a *Jackson v. Virginia* sufficiency-of-the-evidence standard instead of *Kyles v. Whitley* materiality:
- **Orleans Parish Criminal District Court (Pet. App. 5a–6a):** Judge Kimya M. Holmes explicitly applied an outcome-determinative materiality test: *"While I believe they should have turned over that witness's name [Natha Rubin], **I do not believe it changes the outcome of the trial**, that the witness testified did identify Mr. Matthews, I didn't see anything that would change what three (3) other witnesses said, so, I'm going to deny the writ at this time."*
- **Louisiana Court of Appeal, Fourth Circuit (Pet. App. 3a–4a):** The Fourth Circuit recited the exact *Kyles*/*Bagley* standard (*"the evidence is material only if it is reasonably probable that the result of the proceeding would have been different had the evidence been disclosed to the defense. A reasonable probability is one that is sufficient to undermine confidence in the outcome of the trial"*, Pet. App. 4a) before concluding that in light of the strong trial evidence, *"the cumulative impact of the allegedly suppressed evidence fails to cleared [sic] the materiality threshold for establishing a Brady violation."*
- **Supreme Court of Louisiana (Pet. App. 1a–2a):** The state high court did not mention "sufficiency" or "overwhelming" evidence at all, stating simply that *"Applicant fails to show that the state withheld material exculpatory evidence in violation of Brady v. Maryland, 373 U.S. 83 (1963)."*

### 4. Factbound Record With Weak Exculpatory Value
At trial, three neighborhood eyewitnesses who knew Matthews—victim Mark Copeland's best friend Lloyd Martin, 11-year-old Dominique Gibson, and Nira Hood—identified Matthews ("Beaver") as the shooter who stood over Copeland in broad daylight and shot him 13 times following an earlier argument witnessed by Vanessa Henry and admitted by Matthews to police (Pet. 6–8; Pet. App. 57a, 75a, 80a–88a, 147a–153a). By contrast, the undisclosed items in the 1992 NOPD file (Pet. App. 72a–109a)—most notably Natha Rubin's statement that from behind a van that blocked her view of the shooting she saw a "stout young black male," 5'11" to 6', ~220 lbs, walking calmly toward S. Robertson Street whose face she could not identify, and neighborhood canvass notes of two witnesses (Lashane Ezidore and Leroy Milton) who looked out after the shots and "didn't see his face"—neither contradicted the eyewitness identifications nor implicated an alternative suspect. Note that `appendix.txt` contains one pipeline truncation marker at the very end (`[pipeline note: 1,546 characters of this appendix item omitted here, from part-way through PDF page 241 to the end of PDF page 243, to fit the 150,000-character text cap]`), which affected only the tail of Petitioner's compiled list of prior Louisiana cases (Appendix K); all state court rulings and NOPD police file exhibits (Appendices A–J) were provisioned in full.

---

## IV. Justification of Auxiliary Claims and `big_case_score`

- **`relist-increment` (`0.08`):** Because the petition is at its first distribution (`distribution_count == 1`) on a respondent waiver with zero amicus briefs, the vast majority of comparable petitions are denied at the first conference without a CFR or relist. However, because *Brady* petitions from Orleans Parish represented by national appellate counsel (Hogan Lovells) and IPNO occasionally draw a closer look from Justices Jackson or Sotomayor (or a CFR to test the procedural bar), I assign an `8.0%` probability of at least one further distribution.
- **`cvsg-increment` (`0.001`):** Practically zero; the Solicitor General is not invited to file briefs in state post-conviction *Brady* disputes lacking any federal nexus.
- **`summary-disposition-route` (`0.65`):** Conditional on the unlikely event of a grant (`1.5%`), Petitioner explicitly seeks summary reversal on the ground that the Louisiana courts failed to follow *Kyles v. Whitley* (Pet. 31–34). Because *Brady* materiality error-correction petitions from Louisiana (*Wearry v. Cain*, *Smith v. Cain*) are typically resolved by per curiam summary reversal or GVR rather than plenary briefing and oral argument when granted, I set `P(summary disposition | grant) = 0.65`.
- **`dissent-from-denial` (`0.04`) and `order-writers`:** Justice Jackson (joined by Justices Sotomayor and Kagan) dissented from the denial of certiorari in *Brown v. Louisiana*, 143 S. Ct. 886 (2023), on this same legal issue. However, no Justice dissented from the denial of certiorari in *Skinner v. Louisiana*, No. 25-1, in March 2026, and *Matthews* is a much weaker vehicle due to the explicit state procedural bar (`La.C.Cr.P. arts. 930.4 & 930.8`) and non-capital posture. I therefore place `dissent-from-denial` at `0.04`, with per-Justice writing probabilities concentrated on `Jackson` (`0.025`) and `Sotomayor` (`0.020`), `Kagan` (`0.005`), `Gorsuch` (`0.004`), `Thomas` (`0.003`), `Alito` (`0.003`), and `0.002` each for `Roberts`, `Kavanaugh`, and `Barrett`.
- **`big_case_score` (`0.15`):** Decoupled from grant likelihood, this is a fact-intensive state post-conviction challenge to a single 1992 non-capital conviction under settled *Brady*/*Kyles* doctrine, meriting a low-to-modest significance score of `0.15`.
