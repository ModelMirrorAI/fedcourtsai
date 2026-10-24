# Predictor Rationale: *The GEO Group, Inc. v. Nwauzor* (No. 25-828, `evt-brief-sg-disposition`)

## 1. Summary of Forecast

- **Top-level `probability` (`disposition`):** `0.78` (`granted = 1`, `predicted_disposition = "granted"`)
- **Confidence:** `0.82`
- **Big Case Score:** `0.76`
- **Mechanical Claims:**
  - `disposition`: `0.78`
  - `relist-increment`: `0.85`
  - `cvsg-increment`: `0.00`
  - `summary-disposition-route`: `0.04`
  - `dissent-from-denial`: `0.45`

## 2. Base-Rate Anchoring

This cell is a `moment: sg-brief` (`evt-brief-sg-disposition`) forward prediction on a paid cert petition (`sJsonCaseType: "Paid"`, OT2025 docket `25-828`) in the `high` salience band (`sal-v4`, `context.json`).

1. **Salience Band Base Rate (`high` band, prior Terms):**
   From `metrics/statpack.md` (*Segment base rate by salience band (sal-v4)*), the `high` band paid-segment grant-family rate across recent completed Terms is:
   - OT2025: `41.1%` (n=73) [reached `41.1%`, n=73]
   - OT2024: `40.5%` (n=116) [reached `40.5%`, n=116]
   - OT2023: `31.4%` (n=102) [reached `31.4%`, n=102]
   - OT2022: `37.1%` (n=105) [reached `37.1%`, n=105]
   - OT2021: `32.1%` (n=140) [reached `32.1%`, n=140]
   - Pooled across all modern discretionary-cert dockets in the live/historical slice (`Cert petitions by salience band`), the `high` band resolves to `granted 22.9%` + `gvr 12.6%` = `35.5%` grant family (n=971 resolved).

2. **CVSG Cut Base Rate:**
   Per `.github/prompts/predict.md` (*moment: sg-brief*), we anchor on the statpack's CVSG cut (*Cert petitions by CVSG status (paid scored segment)*). Across 164 resolved CVSG petitions in the paid scored segment, the unconditional post-CVSG resolution distribution is:
   - `granted`: `29.3%`
   - `gvr`: `5.5%`
   - **Total Grant Family (`granted` + `gvr`):** **`34.8%`** (n=164 resolved; `denied 62.2%`, `dismissed 3.0%`).

3. **Conditioning on the Solicitor General's Recommendation to Grant:**
   The 34.8% CVSG base rate pools all CVSG petitions regardless of what the Solicitor General ultimately recommends. In empirical Supreme Court practice, the Solicitor General recommends a denial in roughly 75–80% of CVSGs, and when the SG recommends denial, the grant rate is relatively low (~15–20%). Conversely, in the ~15–20% of CVSGs where the Solicitor General unconditionally recommends that the Court **grant** plenary review, the Court follows that recommendation at a very high rate (historically ~70–85%).

## 3. The Solicitor General's Recommendation and Case-Specific Adjustments

### What the Solicitor General Recommended
In `record/documents/sg-invited-brief.txt` (filed September 15, 2026), Solicitor General D. John Sauer explicitly and unconditionally recommends that **"the petition for a writ of certiorari should be granted"** (SG Br. 1, 9, 24). It does not recommend a hold, a GVR, or a partial/conditional grant; it urges full plenary review and reversal ("This Court should grant certiorari and reverse," SG Br. 4).

### Upward Adjustments from the 34.8% Unconditional CVSG Base Rate (+43.2pp to 0.78)
- **Unqualified SG Grant Recommendation (+35pp):** The SG's brief forcefully argues both that the Ninth Circuit's decision is wrong on the merits (violating both the discrimination and direct-regulation prongs of intergovernmental immunity under *United States v. Washington*, 596 U.S. 832 (2022), and conflict/obstacle preemption under `8 U.S.C. § 1231(g)(1)` and `§ 1555(d)`) and that review is urgently needed now with no vehicle obstacles (SG Br. 10–23).
- **Sharp Lower-Court Division and En Banc Dissents (+5pp):** The Ninth Circuit panel divided 2–1 (Judge Bennett dissenting on intergovernmental immunity and preemption), and the Ninth Circuit denied rehearing en banc over the dissents of seven judges (Judge Bennett, plus Judge Collins joined by Judges Nelson and Bress, and Judge Bumatay joined by Judges Callahan and VanDyke). Moreover, the SG and petitioner highlight direct doctrinal conflict with the Third Circuit's decision in *CoreCivic, Inc. v. Governor of New Jersey*, 145 F.4th 315 (3d Cir. 2025) (Bibas, J.), as well as intracircuit tension with *The GEO Group, Inc. v. Newsom*, 50 F.4th 745 (9th Cir. 2022) (en banc), and tension with Second and Fourth Circuit decisions (*United States v. Town of Windsor*, 765 F.2d 16 (2d Cir. 1985); *United States v. Virginia*, 139 F.3d 984 (4th Cir. 1998)).
- **High Stakes, Repeat Advocates, and Clean Vehicle (+5pp):** Petitioner is represented by Paul D. Clement; respondents are the State of Washington (Noah Purcell / Marsha Chien) and a detainee class represented by Gupta Wessler LLP. The case comes on final judgment after jury and bench trials ($17.3M back pay + $5.9M unjust enrichment + permanent injunction that caused suspension of the NWIPC Voluntary Work Program), and the Washington Supreme Court already answered certified state-law questions, leaving zero state-law ambiguity. Furthermore, the SG notes that the United States has consistently opposed Washington's position across three consecutive presidential administrations.

### Downward / Moderating Considerations (-2pp)
- **Respondents' Counterarguments in the BIOs:** In `brief-in-opposition.txt`, Washington and the Nwauzor class argue that (1) GEO's contract with ICE required compliance with state and local labor laws; (2) neither `8 U.S.C. § 1555(d)` nor the 1979 Appropriations Act caps what a private contractor may pay detainees out of its own profits, and GEO occasionally paid up to $5/day; (3) the Washington Supreme Court held that the MWA applies equally to private detention contractors whether contracting with the State or the federal government; and (4) *CoreCivic* involved a total ban on private immigration detention contracts rather than a generally applicable minimum-wage law, and *CoreCivic* itself cited *Nwauzor* as involving a different question (145 F.4th at 329).
- While these arguments give the Court a plausible path to deny if four Justices view the dispute as fact-bound to GEO's specific contract or prefer to see how other minimum-wage challenges percolate, the combination of an explicit SG grant recommendation, seven en banc dissenters, a $23M+ judgment and injunction shuttering a federal detention work program, and the Court's recent sensitivity to Washington laws targeting federal contractors (*United States v. Washington*, 596 U.S. 832 (2022)) makes a grant highly probable. Balancing these factors yields `P(grant) = 0.78`.

## 4. Rationale for Secondary Claims and Big Case Score

- **`relist-increment` (`0.85`):** The snapshot (`2026-09-15.json`) shows `distribution_count = 1` (the April 28, 2026 distribution for the May 14, 2026 conference that produced the CVSG). Now that the SG brief has been filed on September 15, 2026, the Clerk must distribute the petition again for an autumn conference (after the 14-day supplemental brief window under Rule 15.8), and the Court routinely relists at least once before granting. Thus `distribution_count` at resolution is virtually certain to exceed 1, with only a small chance (~15%) of a quirk in docket ingestion or an immediate action without a recorded second distribution.
- **`cvsg-increment` (`0.00`):** A CVSG was already issued on May 18, 2026 (`cvsg_date: "2026-05-18"`), and the SG's brief is already filed. This claim is vacuous by construction on a `moment: sg-brief` cell.
- **`summary-disposition-route` (`0.04`):** Conditional on a grant, plenary review is overwhelmingly the expected route. The SG asks for plenary review, not a GVR, and there is no intervening Supreme Court decision that the Ninth Circuit failed to consider (the Ninth Circuit denied rehearing en banc in August 2025, and while *Menocal* and *Hencely* were decided in early 2026, neither resolves intergovernmental immunity or preemption here). A summary reversal is possible given the strong dissents below, but rare on a complex Supremacy Clause question with certified state-law predicates, placing the conditional summary-disposition probability at 4%.
- **`dissent-from-denial` (`0.45`):** Conditional on the Court denying certiorari despite the SG's recommendation to grant and seven Ninth Circuit judges dissenting from the denial of rehearing en banc, there is a high likelihood (~45%) that at least one conservative Justice would write or note a dissent from denial.
- **`big_case_score` (`0.76`):** If decided on the merits, this case will be a landmark ruling on the scope of intergovernmental immunity and federal preemption for private contractors carrying out federal functions (specifically immigration detention), directly affecting the majority of ICE detention capacity nationwide and resolving how far states can go in regulating federal contractors.
