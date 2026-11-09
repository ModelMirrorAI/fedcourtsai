# Prediction Rationale: *James Owens, et al. v. The Taliban, et al.* (No. 26-294)

**Event:** `evt-order-relist-disposition` (`stage: cert`, `moment: relist`)  
**Forecast:** `granted: 0`, `probability: 0.14`, `predicted_disposition: "denied"`, `big_case_score: 0.78`

---

## 1. Anchor and Base-Rate Calibration

This cell is a `forward`-mode certiorari prediction at `moment: relist`, opened on November 9, 2026 when the Court relisted No. 26-294 for the Conference of November 13, 2026 after its initial distribution for the Conference of November 6, 2026.

From `record/context.json` and `metrics/statpack.md`:
- **Primary Skill Anchor (`cert_anchor`):** `context.json` freezes `band: "elevated"` under `salience_version: "sal-v8"` for `term: 2026`, with `cert_anchor.rate = 0.24813153961136025` (**24.8%**, `lookback_terms: 10`). In `metrics/statpack.md` ("Segment base rate by salience band (sal-v8)"), the nine prior Terms rendered in the table (OT 2017–OT 2025) show bracketed `reached` grant rates in the `elevated` band ranging from `20.9%` (OT 2019, `n=206`) to `27.8%` (OT 2021, `n=230`), pooling to the `24.8%` risk-set anchor.
- **Signal Cuts in `metrics/statpack.md` (Paid Scored Segment):**
  - **Relist count:** In "Cert petitions by relist count (paid scored segment)", petitions ending at `relist_bucket = 1` resolved `denied 85.5%, granted 8.3%, gvr 5.2%, dismissed 1.0%` (`13.5%` grant family over `n=2,532` resolved). Pooling all petitions that reached `1` or more relists (`1`, `2`, and `3+`, totaling `2,532 + 495 + 483 = 3,510` resolved cases) yields a cumulative grant-family (`granted` + `gvr`) rate of **19.5%** (`396.3` granted + `289.2` GVR = `685.5 / 3,510`).
  - **CVSG status:** For `cvsg = none` (`n=13,550` resolved), the grant-family rate is `6.4%` (`granted 4.1%, gvr 2.3%`), versus `34.8%` (`granted 29.3%, gvr 5.5%`) for `cvsg` (`n=164` resolved).
  - **Amicus-brief count:** For `cert_amicus = 1` (`n=1,159` resolved), the grant-family rate is `14.9%` (`granted 10.2%, gvr 4.7%`).
  - **Originating circuit:** In "Modern cert petitions by originating circuit", Second Circuit (`ca2`) petitions resolved `denied 92.6%, granted 2.6%, dismissed 2.5%, gvr 2.4%` (`5.0%` grant family over `n=2,081` resolved).

Starting from the **24.8%** `elevated`-band risk-set anchor (and the **19.5%** pooled `1+` relist rate in the paid scored segment), I adjust downward to **14.0% (`0.14`)** based on the docket posture and the specific legal and vehicle characteristics of No. 26-294 analyzed below.

---

## 2. Docket Progression and Procedural Posture

From `record/snapshots/2026-11-09.json`, `record/context.json`, and `record/related/` (`26-292.json` and `26-293.json`, both carrying `relation: "Vide"`):
- **Distribution Count & Relists:** `distribution_count = 2` (`1` relist, `0` reschedules). All three *vide* petitions (`26-292`, `26-293`, and `26-294`) were docketed on September 4, 2026, distributed on October 21, 2026 for the November 6, 2026 conference, and relisted on November 9, 2026 for the November 13, 2026 conference.
- **No BIO, No Respondent Appearance, and No Call for a Response or CVSG:** The sole named respondent in No. 26-294 is The Taliban, which has defaulted throughout the litigation and has no counsel entered on the Supreme Court docket. Consequently, no Brief in Opposition ("BIO") has been filed, and the Court has issued neither a Call for a Response ("CFR") nor a CVSG (`cvsg_date: null`).
- **Amicus Filings:** On October 7, 2026, Naseer A. Faiq, Chargé d'Affaires of the Permanent Mission of Afghanistan to the United Nations, filed an amicus brief across all three dockets (`26-292`, `26-293`, and `26-294`). On the same day, Iowa and 30 other States filed an amicus brief supporting petitioners in *Havlish* (`26-292`) alone.

**Why this docket progression lowers P(grant):**
In modern Supreme Court practice, the Court virtually never grants plenary review directly off a first conference relist when no respondent has appeared, no BIO is on file, and the Court has not invited the Solicitor General to express the views of the United States. When three related petitions arising from a major consolidated circuit opinion with lengthy en banc dissents are distributed together, a single relist is frequently used to coordinate disposition across the *vide* dockets, consider whether to issue a CVSG, or allow a Justice to circulate a separate statement or dissent respecting denial. Even if the Court were to call for the Solicitor General's views (`cvsg-increment: 0.12`), the United States' institutional position strongly opposes private attachment of the $3.5 billion in blocked Afghan central bank reserves at the FRBNY.

---

## 3. Substantive Assessment of the Petition and Decision Below

The provisioned documents in `record/documents/` include `petition.txt` (40 pages, `empty_text: false`, `ocr_derived: false`), `questions-presented.txt`, and `lower-court-docket.txt`. Because `lower-court-docket.txt` matched only member appeal `23-354` (docket `67110566`) and therefore did not stage `decision-below.txt`, I retrieved the Second Circuit's panel opinion (`Havlish v. Taliban; Aliganga v. Taliban`, 152 F.4th 339 (2d Cir. 2025), `opinion_id: 11127439`) and order denying rehearing en banc (`170 F.4th 100` (2d Cir. 2026), `opinion_id: 11277807`) from the consolidated lead docket (`23-258(L); 23-354(L)`) via the CourtListener MCP server.

### A. Subordinate Vehicle Relative to Companion Petitions Nos. 26-292 (*Havlish*) and 26-293 (*Ashton*)
The Second Circuit litigation consolidated two fundamentally different groups of plaintiffs seeking to reach the $3.5 billion in Da Afghanistan Bank ("DAB") reserves frozen at the FRBNY after the Taliban's August 15, 2021 takeover of Kabul:
1. **Judgment Plaintiffs (*Havlish*, No. 26-292, and *Ashton*, No. 26-293):** September 11 victims who already held final default judgments against the Taliban and moved for post-judgment turnover under Section 201(a) of the Terrorism Risk Insurance Act ("TRIA"), 28 U.S.C. § 1610 note. The Second Circuit panel unanimously held (following *Bank Markazi v. Peterson*, 578 U.S. 212, 217 n.2 (2016), and *Weinstein v. Islamic Republic of Iran*, 609 F.3d 43 (2d Cir. 2010)) that TRIA § 201(a) **abrogates both jurisdictional and execution immunity under the FSIA**, including central-bank immunity under 28 U.S.C. § 1611(b)(1). The Judgment Plaintiffs lost only because the panel majority held (2–1) that an entity's status as a terrorist "agency or instrumentality" under the TRIA must be measured on the date the assets were blocked (August 15, 2021) rather than when turnover is sought.
2. **Pre-Judgment Plaintiffs (*Owens*, No. 26-294):** Victims of the 1998 East Africa U.S. Embassy bombings who did not file suit against the Taliban until March 8, 2022, and sought an *ex parte* pre-judgment attachment under Fed. R. Civ. P. 64 and N.Y. CPLR § 6201. Because they held no judgment when seeking attachment, they could not invoke TRIA § 201(a) and instead had to argue that DAB enjoys no baseline immunity under the FSIA (`28 U.S.C. §§ 1603, 1609, 1611(b)(1)`).

This distinction makes No. 26-294 a substantially weaker vehicle than Nos. 26-292 and 26-293:
- If the Court wishes to address whether terrorism victims may execute against the $3.5 billion in DAB reserves, *Havlish* (backed by 31 State amici) and *Ashton* present a clean, post-judgment statutory question under TRIA § 201(a) on which all five Second Circuit dissenters agreed—without requiring the Court to strip a recognized nation's central bank of baseline FSIA immunity or trench upon the President's recognition power.
- *Owens* arises in an interlocutory posture from the vacatur of a state-law pre-judgment attachment, and unlike in *Havlish* and *Ashton*, the garnishee FRBNY was not even a party to the *Owens* appeal (`23-354`).

### B. Flaws in Question Presented 1 (FSIA Interpretation vs. Executive Recognition)
Petitioners' first Question Presented asks whether the FSIA requires courts to independently interpret its provisions rather than "defer to State Department websites and Department of Justice litigation filings in determining whether an entity is entitled to sovereign immunity under the FSIA." (`questions-presented.txt`; `petition.txt` at i).
- **No Deference on § 1603(b) Agency-or-Instrumentality Status:** In footnote 97 of the panel opinion (`152 F.4th at 357 n.97`), Judges Cabranes and Calabresi explicitly agreed with the *Owens* petitioners "that the Judiciary cannot rely on an articulation by the Executive to resolve the matter of agencies or instrumentalities under the FSIA," and rested their § 1603(b)(2) holding instead on Article 27.2 of the 2003 Afghanistan Bank Law, under which 100% of DAB's capital belongs to the State of Afghanistan.
- **Split Among the En Banc Dissenters on *Zivotofsky* and § 1603(a):** On the threshold question whether the State of Afghanistan remains a "foreign state" under § 1603(a), Judge Menashi (one of the five en banc dissenters) wrote separately (`170 F.4th at 110–16`) to agree with the panel majority and Judges Nardini and Lohier that the President's formal recognition of Afghanistan as an independent state is conclusive under *Zivotofsky ex rel. Zivotofsky v. Kerry*, 576 U.S. 1 (2015), and that reading the FSIA to allow courts to derecognize a recognized foreign state would be unconstitutional.
- **No Genuine Circuit Split:** None of the circuit decisions petitioners cite (*OI European Group B.V. v. Bolivarian Republic of Venezuela*, 73 F.4th 157 (3d Cir. 2023); *Ungar v. Palestine Liberation Organization*, 402 F.3d 274 (1st Cir. 2005); *Kirschenbaum v. 650 Fifth Avenue & Related Properties*, 830 F.3d 107 (2d Cir. 2016)) held that a nation formally recognized by the President ceases to be a "foreign state" under § 1603(a) or that its statutory central bank loses § 1603(b)(2) ownership status when an unrecognized regime seizes power.

### C. Weakness of Question Presented 2 (*Sua Sponte* Attachment Immunity)
Petitioners' second Question Presented asks whether a federal court may raise FSIA attachment immunity *sua sponte* when threshold facts are disputed and no sovereign has appeared.
- Every judge on the Second Circuit—including Judge Sullivan in his panel concurrence/dissent (`152 F.4th at 366 n.1`) and all five en banc dissenters—agreed that district courts may apply 28 U.S.C. §§ 1609 and 1611(b)(1) *sua sponte* because those provisions state in mandatory terms that foreign sovereign and central-bank property "shall be immune from attachment."
- That holding accords with every circuit to decide the issue, including *Walters v. Industrial & Commercial Bank of China, Ltd.*, 651 F.3d 280, 291–94 (2d Cir. 2011), *Rubin v. Islamic Republic of Iran*, 637 F.3d 783, 799–801 (7th Cir. 2011), *aff'd*, 583 U.S. 202 (2018), and *Walker International Holdings Ltd. v. Republic of Congo*, 395 F.3d 229, 233 (5th Cir. 2004). Moreover, petitioners received a full opportunity to brief and submit factual evidence on their motion to confirm the *ex parte* attachment before the district court vacated it.

---

## 4. Corpus Priors (`fedcourts query`)

I queried the corpus for recent 2020s SCOTUS granted and denied petitions and the companion *vide* dockets:
- `fedcourts query --court scotus --era 2020s --disposition granted --limit 10` showed that recent OT 2026 non-federal grants (such as *Goldman Sachs Bank USA v. Brown*, No. 25-1408, `distribution_count: 4`; *Association for Education Fairness v. Montgomery County Board of Education*, No. 26-12, `distribution_count: 3`; *Berry v. United States*, No. 25-7026, `distribution_count: 5`; and *Missionaries of Saint John the Baptist, Inc. v. Frederic*, No. 25-1131, `distribution_count: 2` with 16 amicus briefs) all featured an adversarial respondent appearance and a Brief in Opposition on file prior to grant.
- `fedcourts query --court scotus --era 2020s --disposition denied --limit 10` showed multiple petitions denied on November 9, 2026 after `distribution_count: 2` (1 relist), including *Westcott v. Voice of the Experienced* (No. 26-18), *Walls v. Prince George's County* (No. 26-107, denied after 1 relist with 6 amicus briefs), and *Cup Foods, Inc. v. City of Minneapolis* (No. 26-222).
- `fedcourts query --court scotus --docket-number 26-292` and `--docket-number 26-293` confirmed that both *vide* companions share the same `distribution_count: 2` and lack of a response request or CVSG, while No. 26-292 (*Havlish*) additionally carries the 31-state amicus brief.

---

## 5. Summary of Claim Probabilities and Uncertainties

- **`disposition` (`0.14`):** Anchored on `24.8%` (`cert_anchor`) and `19.5%` (pooled `1+` relists), adjusted down for the absence of a BIO/CFR/CVSG, lack of a circuit split, strong foreign-affairs/central-bank immunity headwinds, and inferior pre-judgment vehicle status relative to Nos. 26-292 and 26-293, balanced against the $3.5B stakes and five en banc dissents below.
- **`relist-increment` (`0.30`):** Modest chance of at least one further distribution beyond `distribution_count: 2`, either to accommodate circulation of a separate statement/dissent from denial or if the Court orders a CVSG.
- **`cvsg-increment` (`0.12`):** Low-to-moderate chance the Court invites the Solicitor General's views given the default of the Taliban and the foreign-relations stakes, tempered by the fact that the Executive Branch's opposition to attachment is already clear from the record below.
- **`summary-disposition-route` (`0.05`):** Conditional on a grant, summary reversal or GVR is very unlikely given the magnitude and complexity of the case.
- **`dissent-from-denial` (`0.18`) & `order-writers`:** Elevated chance (`18%`) of a written dissent or statement respecting denial given the 5-judge en banc dissent below on *Loper Bright*, *Samantar*, and terrorism victims' remedies, concentrated on Justices Gorsuch (`0.07`), Thomas (`0.06`), and Alito (`0.06`).
- **Main Uncertainty:** Whether the Court treats all three *vide* petitions (`26-292`, `26-293`, and `26-294`) as a single package and either calls for the Solicitor General's views or grants all three together to preserve every statutory theory (both TRIA and FSIA) for merits review.
