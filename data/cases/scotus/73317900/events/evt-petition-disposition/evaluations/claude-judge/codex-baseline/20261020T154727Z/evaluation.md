# codex-baseline: P(grant) 0.68, predicted `gvr`. Correct, Brier 0.1024

**What it got right.** It found the decisive route: the petition was principally a GVR request, and *Jules* had since been decided. It read the *Jules* opinion itself (slip op. 6-8) and tied that opinion's reasoning about retained jurisdiction to the petition's anchor theory. It treated the call for a response after the waiver as a signal of attention. It named the GVR label exactly, and it correctly noted that a GVR counts as a grant even if the petitioner later loses on remand.

**Weaknesses.** It never read the brief in opposition or the supplemental brief, which were not provisioned. It acknowledged that gap honestly, but it left the respondent's main counter (that Section 4's "civil action" text is an independent ground) only gestured at. Its move from about 5% to 68% is large and rests mostly on one inference. That inference proved right and was well argued, with counterweights stated: the Section 1782 / Section 4 distinction, and the Third Circuit's own *George* decision on the Section 9/10 split. Its base-rate handling (pooling pre-2025 Terms in the frozen band) was sound and clearly caveated.

`reasoning_quality` 0.75: the analysis was sound and correctly weighted, held back from top marks by a thin engagement with the opposing argument.

## The cell

Cert stage, forward mode. *Burford German Funding LLC v. financialright claims GmbH* (No. 25-1269, from the Third Circuit). Outcome: **GVR** (`actual_granted` = 1), resolved 2026-10-19 after two distributions. All three candidates predicted on 2026-09-16 from the same snapshot: one distribution, a response requested on July 15 after the respondent waived, and the brief in opposition submitted September 14. Each prediction froze `band: baseline` under `sal-v4`, so the **stamped segment base rate** (risk-set anchor) and the Brier skill are the harness's. I leave them null and quote no rate of my own. No semantic set is declared on a cert cell, and votes are not scored at this stage.

The way to read this petition was to see that it was a request to hold the case and GVR in light of *Jules v. Andre Balazs Properties* (decided 2026-05-14). The call for a response after a waiver, coming after *Jules* was decided, was the strongest signal on the docket. The Court did GVR.

**Leakage.** All three are forward cells, and the case was open when they predicted. No call reached material dated on or after the resolution, and no prose treats the outcome as known. `influenced_prediction` = `not_applicable` for all three. Details are in each `leakage.notes`.
