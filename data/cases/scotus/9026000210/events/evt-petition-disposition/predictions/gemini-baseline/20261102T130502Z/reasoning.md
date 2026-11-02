# Cert-Stage Prediction: *Donald J. Trump, President of the United States, et al. v. Neeta Thakur, et al.*, No. 26-210

## I. Overview and Procedural Posture

In *Trump v. Thakur* (No. 26-210), the Solicitor General petitions for a writ of certiorari to review a published opinion of the United States Court of Appeals for the Ninth Circuit (*Thakur v. Trump*, 179 F.4th 1042 (9th Cir. May 26, 2026), authored by Judge Christen and joined by Judges Gould and Desai). The Ninth Circuit affirmed a preliminary injunction entered by Judge Rita F. Lin of the Northern District of California (*Thakur v. Trump*, 789 F. Supp. 3d 809 (N.D. Cal. June 24, 2025)) requiring the National Science Foundation (NSF) and the National Endowment for the Humanities (NEH) to reinstate competitive academic research grants that had been terminated pursuant to Executive Order 14151 ("Ending Radical and Wasteful Government DEI Programs and Preferencing," 90 Fed. Reg. 8339) and Executive Order 14173 ("Ending Illegal Discrimination and Restoring Merit-Based Opportunity," 90 Fed. Reg. 8633).

The sole Question Presented in the petition is:
> "Whether the First Amendment prohibits the government from considering the viewpoints furthered by academic research projects when deciding whether to grant or terminate funding for those projects through competitive grant programs."

The petition was docketed on August 19, 2026. After one 30-day extension, respondents (a provisionally certified class of University of California researchers, represented by Erwin Chemerinsky and Lieff Cabraser Heimann & Bernstein) filed their Brief in Opposition on October 15, 2026. The Solicitor General filed a Reply Brief on October 28, 2026, and the case was distributed on October 28, 2026, for the Conference of November 13, 2026 (`distribution_count = 1`). No amicus briefs were filed at the certiorari stage (`amicus_briefs = null`).

---

## II. Baseline Anchor and Decomposition Framework

### 1. Risk-Set Band Anchor
From `record/context.json` and `metrics/statpack.md`, this petition sits in the **`federal`** salience band (`band = "federal"`), because the petitioner is the President of the United States and federal agencies represented by the Solicitor General. Over the 10-Term lookback window (OT2016–OT2025), the pooled grant-family rate for distributed petitions in the `federal` band is:
- **`anchor_rate` = 0.7339901477832512** (149 of 203 resolved petitions, or **73.4%**).
- Across recent individual Terms in `metrics/statpack.md`, the `federal` band grant rate has been consistently high: 80.0% in OT2025 (24/30), 69.2% in OT2024 (9/13), 85.0% in OT2023 (17/20), 66.7% in OT2022 (8/12), and 73.7% in OT2021 (14/19).

### 2. Relist-Count Cross-Check
At `distribution_count = 1`, this petition is entering its first Conference (November 13, 2026). As `metrics/statpack.md` ("Cert grant rate by relist count") shows, across all distributed petitions in OT2025, 0-relist (single-distribution) cases had a 0.2% grant rate (6/2,832), whereas cases relisted at least once (`1` relist: 15/46 = 32.6%; `2` relists: 14/36 = 38.9%; `3` relists: 2/12 = 16.7%; `4+` relists: 5/26 = 19.2%) accounted for the vast majority of plenary grants and GVRs. Because the Court's modern practice is to relist nearly all grant-worthy petitions at least once to check for vehicle defects before granting certiorari—and because SG petitions frequently receive at least one relist before a grant or denial—the probability of a relist increment from `distribution_count = 1` (`relist-increment`) is high (**0.72**).

---

## III. Case-Specific Adjustments from the Federal Anchor

Starting from the 73.4% (`0.734`) federal-petitioner base rate, I evaluate the doctrinal, institutional, and procedural factors that pull the probability of certiorari up or down.

### A. Factors Favoring Certiorari (Supporting the High Federal Base Rate)

1. **Solicitor General Petition Challenging Invalidation of Major Executive Branch Policy:**
   The Solicitor General rarely petitions for certiorari unless the decision below seriously impairs federal administration or conflicts with Supreme Court precedent. Here, the Ninth Circuit's published opinion holds that the First Amendment prohibits federal agencies from terminating competitive research grants on the ground that the funded research projects promote diversity, equity, and inclusion (DEI). Although the injunction below directly covers UC researchers' grants from NSF and NEH, the Ninth Circuit's constitutional holding applies circuit-wide to competitive research grant programs across the federal government.

2. **Substantial Doctrinal Tension with *Finley*, *Rust*, and *Regan*:**
   The Solicitor General mounts a forceful merits argument that the Ninth Circuit turned *National Endowment for the Arts v. Finley*, 524 U.S. 569 (1998), upside down. In *Finley*, the Court held that competitive grantmaking inherently requires selective judgments where the government acts as patron rather than sovereign, distinguished competitive subsidies from neutral student-activity funds (*Rosenberger v. Rector & Visitors of Univ. of Va.*, 515 U.S. 819 (1995)), and rejected a First Amendment challenge to the NEA's "decency and respect" criteria. While *Finley* contained caveats noting that the NEA had not engaged in "invidious viewpoint discrimination" or "suppression of dangerous ideas" (524 U.S. at 587), the Ninth Circuit treated those caveats as a categorical holding that viewpoint-based selection or termination within a competitive academic research program violates the First Amendment. The SG also points to *Rust v. Sullivan*, 500 U.S. 173 (1991), and *Agency for International Development v. Alliance for Open Society International, Inc. (AOSI)*, 570 U.S. 205 (2013), arguing that while the government cannot leverage funding to regulate a grantee's speech *outside* the funded program, defining which projects to fund *within* a program is permissible policy selection rather than unconstitutional coercion. Several Justices on the current Court are likely to view the Ninth Circuit's application of *Rosenberger* to competitive federal research grants as an overbroad constitutionalization of federal spending priorities.

3. **Clean Legal Framing in the Question Presented:**
   The Solicitor General deliberately dropped the threshold Tucker Act / APA arguments that had divided the lower courts and chose to present a single, pure question of First Amendment law. Respondents do not dispute that the First Amendment question was squarely pressed and passed upon by both the district court and the Ninth Circuit.

### B. Factors Weighing Against Certiorari (Pulling Below the 73.4% Anchor)

Despite the strong federal-petitioner prior, four significant case-specific considerations weigh against granting plenary review on this petition:

1. **Absence of a Square Circuit Split:**
   The Solicitor General does not claim a direct circuit conflict on the Question Presented, instead arguing that the Ninth Circuit's decision is in "serious tension" with the Fourth Circuit's decision in *National Association of Diversity Officers in Higher Education (NADOHE) v. Trump*, 167 F.4th 252 (4th Cir. Feb. 6, 2026). Inspection of the *NADOHE* opinion (via CourtListener MCP, Opinion ID 11252285) confirms respondents' point in the Brief in Opposition: *NADOHE* involved a *facial* challenge to EOs 14151 and 14173. With respect to the Termination Provision of EO 14151, the plaintiffs in *NADOHE* brought only a Fifth Amendment facial vagueness challenge (not a First Amendment challenge), and the Fourth Circuit explicitly noted that "if government actors have terminated grants or contracts 'without regard to their legality,' then plaintiffs can sue those actors for terminating those contracts" in an as-applied challenge. Meanwhile, the one appellate case raising the exact same First Amendment challenge to NEH's grant terminations—*American Council of Learned Societies v. McDonald*, No. 25-2481 (2d Cir.)—remains pending in the Second Circuit without a decision as of November 2, 2026. The Court may prefer to allow the Second Circuit (and other circuits) to weigh in before granting review.

2. **Interlocutory Posture and Imminent District Court Summary Judgment Proceedings:**
   This petition arises from an interlocutory appeal of a preliminary injunction entered in June 2025 on an expedited record (19 days after the complaint was filed). As respondents emphasize in the Brief in Opposition (and as confirmed by the Northern District of California docket in *Thakur v. Trump*, No. 3:25-cv-04737, via CourtListener MCP), the litigation in the district court has advanced to final summary judgment and class certification across 14 federal agencies, with the summary judgment hearing scheduled for November 17, 2026—just four days after this petition's first Conference. Moreover, one original preliminary-injunction agency (EPA) has already entered into a class action settlement preliminarily approved on October 1, 2026 (with final approval set for December 10, 2026). Granting certiorari on an interlocutory two-agency preliminary injunction when a final judgment on a full administrative record is imminent risks procedural complications or mootness of the preliminary injunction.

3. **Prior Denial of Emergency Stay Application in *NIH v. APHA* Reference:**
   As the Ninth Circuit opinion notes (Pet. App. 20a–22a) and respondents highlight (BIO 1, 8–9), in *National Institutes of Health v. American Public Health Association*, 145 S. Ct. 2658 (Aug. 21, 2025) (No. 25A103), the Supreme Court stayed an APA vacatur of NIH grant terminations on Tucker Act grounds, and the Solicitor General expressly pointed to the *Thakur* preliminary injunction to urge the Court to reject a First Amendment exception to the Tucker Act—yet five Justices (including Justice Barrett in her controlling concurrence) declined to disturb the *Thakur* approach, distinguishing constitutional claims from APA/contract claims. While the SG is not re-raising the Tucker Act issue here, the Court's willingness to leave the *Thakur* preliminary injunction intact during the summer of 2025 suggests less institutional urgency to intervene at the preliminary-injunction stage than in cases where the Court previously granted emergency stays.

4. **Vehicle Nuances (Retroactive Mid-Stream Termination vs. Initial Competitive Selection):**
   The SG's Question Presented groups together "deciding whether to grant or terminate funding," because the SG's legal theory under *Finley* depends on treating mid-stream grant terminations the same as initial competitive award decisions. Respondents argue that this case involves only the retroactive termination of *already awarded* multi-year grants where Congress statutorily mandated that NSF and NEH insulate grantmaking from political interference and where 2 C.F.R. § 200.340(a)(4) required agencies to specify priority-termination terms in the award (which NSF and NEH had not done). Even Justices sympathetic to the SG's view of *Finley* for initial grant selection may hesitate to use an interlocutory mid-stream termination case—complicated by parallel APA/regulatory holdings below—as the vehicle to announce a broad First Amendment rule for competitive grant programs.

---

## IV. Synthesis and Probability Calibration

Weighing these considerations:
- The **73.4% (`0.734`) `federal` band base rate** is a powerful empirical anchor: when the Solicitor General asks the Supreme Court to review a published court of appeals decision holding federal executive action unconstitutional under the First Amendment, the Court grants certiorari more often than not.
- However, the combination of **(1) interlocutory preliminary-injunction posture with summary judgment hearing days away in the district court**, **(2) no square circuit conflict yet (with the Second Circuit's decision in *ACLS* still pending)**, and **(3) the specific mid-stream termination / parallel APA posture** pulls the grant probability meaningfully downward from the 73.4% federal-petitioner average.
- Balancing the SG's institutional weight and the importance of the First Amendment / Executive Order 14151 issue against the interlocutory vehicle and absence of a split, I calibrate the overall grant-family probability at **0.56** (**56%**):
  - **`full-grant` (`granted`)**: **0.55** — Most likely single outcome; the Court often grants SG petitions challenging circuit-wide constitutional injunctions even without a circuit split.
  - **`gvr`**: **0.01** — Small probability that the Court holds the petition and later GVRs if intervening developments warrant remand.
  - **`summary-reversal`**: **0.00** — Practically zero; the Court does not summarily reverse on complex, novel First Amendment questions where *Finley* and *Rosenberger* intersect.
  - **`denied`**: **0.42** — Substantial probability that the Court denies certiorari because of the interlocutory posture, lack of a circuit split, and ongoing summary judgment proceedings in the district court.
  - **`dismissed`**: **0.02** — Small chance that the petition is dismissed under Rule 46 if final judgment or settlement in the district court supersedes the preliminary injunction before the Court acts.
  - **`separate-writing-on-denial`**: **0.08** — Conditional on denial (or overall), there is a modest chance (~18–20% conditional on denial, ~8% unconditional) that one or more conservative Justices (e.g., Justice Thomas or Justice Alito) write a statement or dissent from the denial of certiorari emphasizing that the denial of interlocutory review does not endorse the Ninth Circuit's reading of *Finley*.
