# claude-baseline: P(grant) 0.13, predicted denied

**Cell.** Cert stage, forward mode. The Court denied the petition on 2026-10-13 (`actual_disposition` denied, `actual_granted` 0), with one distribution, no CVSG, no relist and no noted dissent. All three candidates predicted `denied`, so `correct` = 1 for each. The prediction froze `band: baseline` under `sal-v4`, so this is a frozen-band cert cell: the harness stamps the segment base rate (the risk-set anchor), the Brier skill score and the basis. I leave all three null and quote no rate of my own here. The claims block is scored in code and is not graded here. No semantic set is declared on a cert cell, so no `semantic_grades` block is written.

**Leakage.** The log mode is `forward`. The prediction was made 2026-10-04, nine days before the 2026-10-13 denial, so the outcome did not exist yet. Nothing in the log or the prose shows this petition's disposition surfacing. `influenced_prediction` = `not_applicable`, `leakage_suspected` = false.

**Score.** Brier = 0.13² = 0.0169.

**Reasoning quality: 0.75.** This is the most thorough and best-structured analysis of the three:
- **Right anchor.** It pools the reached baseline rate, explains why that rate rather than the terminal one, and uses the relist and circuit cuts only to show the shape of the population.
- **Concrete case-specific reasons against a grant.** No split, conceded. The Court's 2024 denial in Bohon, a near-direct prior denial. MCorp on the materially identical 1818(i)(1). A unanimous panel, with rehearing en banc denied without a vote. QP 2 has no lower-court support. A weak vehicle.
- **Explicit decomposition.** It splits the grant family into a plenary grant (≈0.05) plus a GVR after a Johnson hold (≈0.25 × 0.4). That makes the main source of uncertainty easy to check.

Its own list of reasons against a grant argues for a lower number than 0.13, and the hold probability, which it calls its "softest number", carries most of the excess. The outcome (a denial at the first conference, with no hold) suggests the hold path was overpriced. Still, the reasoning is transparent, internally consistent, and correct about why denial was likely. It also discloses the throttled retrieval and the coverage gap in the corpus query.
