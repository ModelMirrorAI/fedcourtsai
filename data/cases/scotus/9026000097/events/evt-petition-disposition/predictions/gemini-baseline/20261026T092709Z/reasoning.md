# Predictor Reasoning and Calibration: *Hellman v. Craven*, No. 26-97

## 1. Case Overview and Procedural Posture

- **Case**: *Ariella Hellman, on Their Own Behalf and as Next Friend of Their Child, E. H., et al. v. Katherine Craven, Chair, Massachusetts Board of Elementary and Secondary Education, et al.*, No. 26-97 (`scotus/9026000097`).
- **Event**: `evt-petition-disposition` (cert stage, distribution moment, forward mode).
- **Originating Court**: U.S. Court of Appeals for the First Circuit (`ca1`, No. 25-1417), *Hellman v. Craven*, 168 F.4th 255 (1st Cir. Feb. 20, 2026) (Barron, C.J., joined by Lynch and Kayatta, JJ.), affirming Rule 12(b)(6) dismissal by the U.S. District Court for the District of Massachusetts (Kelley, J.).
- **Question Presented**: "Does the unconstitutional conditions doctrine apply to the right, recognized in *Pierce v. Society of Sisters*, to send one's child to a private school?"
- **Docket Signals at Snapshot (`2026-10-26.json`)**:
  - Paid petition docketed July 21, 2026.
  - Counsel for Petitioners: David Gilbert Hodges (Institute for Justice).
  - Seven cert-stage amicus briefs filed August 19–21, 2026: (1) Foundation for Excellence in Education, Inc.; (2) Center for the Rights of Abused Children; (3) Prof. Charles L. Glenn; (4) Council for American Private Education & Agudath Israel of America; (5) West Virginia, South Carolina, and 12 Other States; (6) Alliance Defending Freedom; (7) New Civil Liberties Alliance.
  - Respondents' waiver of right to respond submitted September 24, 2026 (docketed October 1, 2026).
  - Distributed October 7, 2026 for the Conference of October 23, 2026 (`distribution_count: 1`).
  - No response requested (`response_requested: null`), no CVSG (`cvsg_date: null`), `band: "baseline"` (`salience_version: "sal-v4"`).

## 2. Base-Rate Anchor and Calibration

From `metrics/statpack.md` (rendered against the OT2017–OT2026 corpus), the paid modern-cert baseline salience band (`sal-v4`) carries an unweighted pooled grant rate of approximately **0.9%–1.1%** across strictly-prior Terms OT2017–OT2025:
- OT2025: 1.0% (14/1,467)
- OT2024: 1.1% (14/1,284)
- OT2023: 0.7% (10/1,347)
- OT2022: 0.8% (9/1,160)
- OT2021: 0.9% (12/1,367)
- OT2020: 1.3% (18/1,390)
- OT2019: 0.6% (8/1,366)
- OT2018: 0.9% (14/1,515)
- OT2017: 0.9% (13/1,426)

Pooling OT2017–OT2025 in the baseline band yields 112 grants over 12,322 resolved paid baseline petitions (**0.91%**).

Why adjust slightly upward from ~0.91% to **1.5% (`probability: 0.015`, `grant_likelihood_tier: "unlikely"`)**?
- **Upward factors**: The petition is litigated by a prominent Supreme Court public-interest litigator (Institute for Justice) on a clean Rule 12(b)(6) record and is supported by seven cert-stage amicus briefs, including a 14-state coalition and well-known repeat-player amici (ADF, NCLA, Agudath Israel). In the statpack's amicus cut, petitions with 4+ cert-stage amicus briefs have a much higher grant rate when a response is filed or requested.
- **Downward / capping factors**: Respondents waived their right to respond on September 24, 2026, and the petition went to the October 23, 2026 conference on its first distribution (`distribution_count = 1`) **without a Call for a Response (CFR)**. Under Supreme Court practice, the Court almost never grants plenary review (or even summary disposition) off a waiver without first issuing a CFR. While it remains possible that the Court could issue a post-conference CFR or relist, the overwhelming majority of single-distribution petitions with a waiver and no pre-conference CFR are denied outright on the Monday order list following the conference (here, October 26, 2026). Even if a CFR were belatedly issued, the substantive merits face an uphill climb because there is no genuine circuit conflict on whether *Pierce* requires states to provide state-funded special-education services to private-school students or triggers strict scrutiny under the unconstitutional conditions doctrine for neutral public-school enrollment requirements.

Balancing the high amicus count against the decisive absence of a pre-conference CFR and the lack of a true circuit split places the overall grant probability at **0.015** (`unlikely` tier, 1%–5%).

## 3. Mechanical Claims Calibration (`cert-v3`)

- **`disposition` (`0.015`)**: Must match top-level `probability`.
- **`relist-increment` (`0.22`)**: The general single-distribution relist hazard in the paid scored segment is ~26.3% (`docs/outcome-decomposition.md`). Here, because Respondents waived and no CFR issued before the conference, most cases in this posture are simply denied after the first conference; however, the presence of seven amicus briefs (including 14 States) and IJ representation creates a real chance that a chambers flags the petition for a post-conference CFR or a brief hold/relist, warranting a 0.22 probability.
- **`cvsg-increment` (`0.005`)**: This is a Fourteenth Amendment substantive due process challenge to a state special-education regulation, with no federal IDEA claim pleaded. The probability of a CVSG is very low (0.5%).
- **`summary-disposition-route` (`0.25`)**: Conditioned on a grant, the prior-Term paid-grant cert-order disposition baseline is ~35.4% (`docs/outcome-decomposition.md`). Because Petitioners ask the Court to resolve a major constitutional question of first impression—whether *Carson*/*Espinoza*/*Trinity Lutheran*'s unconstitutional-conditions framework extends beyond the Free Exercise Clause to the *Pierce* substantive due process right—a grant would almost certainly be for plenary merits review (75%) rather than a summary GVR or summary reversal (25%).
- **`dissent-from-denial` (`0.04`)**: Conditioned on denial, there is a small (~4%) chance that one or more conservative Justices (most plausibly Thomas, Alito, or Gorsuch) note a dissent or statement respecting denial given the school-choice / parental-rights subject matter, though a noted dissent rarely occurs without a prior CFR and relist.
- **`order-writers`**: Per-Justice probabilities for writing on the cert order reflect the baseline rarity of cert-order writings (~0.1%–0.2% for most Justices, elevated to 1.2%–1.5% for Thomas, Alito, and Gorsuch who most frequently author dissents from denial in parental-rights and religious/educational liberty cases).
