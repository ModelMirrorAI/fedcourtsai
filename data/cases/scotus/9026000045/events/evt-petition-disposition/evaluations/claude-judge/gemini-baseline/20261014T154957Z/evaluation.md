# gemini-baseline: P(grant) 0.01, predicted denied

**Cell.** Cert stage, forward mode. The Court denied the petition on 2026-10-13 (`actual_disposition` denied, `actual_granted` 0), with one distribution, no CVSG, no relist and no noted dissent. All three candidates predicted `denied`, so `correct` = 1 for each. The prediction froze `band: baseline` under `sal-v4`, so this is a frozen-band cert cell: the harness stamps the segment base rate (the risk-set anchor), the Brier skill score and the basis. I leave all three null and quote no rate of my own here. The claims block is scored in code and is not graded here. No semantic set is declared on a cert cell, so no `semantic_grades` block is written.

**Leakage.** The log mode is `forward`. The prediction was made 2026-10-04, nine days before the 2026-10-13 denial, so the outcome did not exist yet. Nothing in the log or the prose shows this petition's disposition surfacing. `influenced_prediction` = `not_applicable`, `leakage_suspected` = false.

**Score.** Brier = 0.01² = 0.0001.

**Reasoning quality: 0.55.** The core analysis points the right way, and the Court's denial bears it out. The briefs concede there is no inter-circuit split. The Fifth Circuit's express-preclusion reading matches Bohon and Azimov. The SG is a party in opposition. For these reasons the CVSG claim is near zero. The weaknesses:
- **Wrong anchor.** It says the baseline band "historically carries a grant rate between 0.5% and 2%". That matches the statpack's *terminal* baseline figures. A petition still at its first distribution faces the *reached* (risk-set) rate, which is about 4–6% per prior Term, and the statpack caption says that is the figure a frozen band is scored against. The final 1% happened to be the best-calibrated number in the panel, but it rests on a misread anchor.
- **Missing argument.** It never engages the petition's alternative request to hold the case for Johnson v. United States Congress. That was the main live route to a non-denial, and the SG's brief spent a section opposing it.
- **Muddled detail.** It calls the earlier disagreement a "resolved intra-circuit conflict". The briefs describe a district-court disagreement, not an appellate one.
- **Thin case-specific reasoning.** MCorp, which the other candidates use, goes unmentioned.
