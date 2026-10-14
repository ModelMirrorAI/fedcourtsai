# codex-baseline: P(grant) 0.10, predicted denied

**Cell.** Cert stage, forward mode. The Court denied the petition on 2026-10-13 (`actual_disposition` denied, `actual_granted` 0), with one distribution, no CVSG, no relist and no noted dissent. All three candidates predicted `denied`, so `correct` = 1 for each. The prediction froze `band: baseline` under `sal-v4`, so this is a frozen-band cert cell: the harness stamps the segment base rate (the risk-set anchor), the Brier skill score and the basis. I leave all three null and quote no rate of my own here. The claims block is scored in code and is not graded here. No semantic set is declared on a cert cell, so no `semantic_grades` block is written.

**Leakage.** The log mode is `forward`. The prediction was made 2026-10-04, nine days before the 2026-10-13 denial, so the outcome did not exist yet. Nothing in the log or the prose shows this petition's disposition surfacing. `influenced_prediction` = `not_applicable`, `leakage_suspected` = false.

**Score.** Brier = 0.10² = 0.01.

**Reasoning quality: 0.72.** Strengths:
- **Right anchor.** It uses the reached baseline figures, pooled strictly before OT2026 and weighted by resolved count. It explains why the terminal no-relist rate is not the right number.
- **Balanced reading of the briefs.** Pushing up: the Axon "irreparable here-and-now injury" theory and the Johnson hold request. Pushing down: the explicit-versus-implicit preclusion distinction, MCorp, the conceded absence of a split, and rehearing denied with no vote requested.
- **Honest about limits.** It flags that the reply and amicus texts were missing and that external verification was degraded.

Weakness: doubling the anchor to 10% is under-supported once it has conceded no split and a stayed agency proceeding (no urgency). The hold adjustment also stays loose; it is described in words but never decomposed. Denial was strongly favored, as the analysis itself concludes, so the reasoning is sound but somewhat too generous to the grant side.
