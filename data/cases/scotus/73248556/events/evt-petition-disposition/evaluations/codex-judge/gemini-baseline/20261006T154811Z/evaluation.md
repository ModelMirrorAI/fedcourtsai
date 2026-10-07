# Evaluation: gemini-baseline

## Outcome and numerical scores

This is a cert-stage petition disposition. The supplied outcome records denial on October 5, 2026, with `actual_granted = 0`. gemini-baseline's latest staged prediction calls `denied` and assigns 0.05 to any grant. The exact-label score is **1**, and the Brier score is **(0.05 - 0)^2 = 0.0025**. A correct denial does not establish the Court's substantive reasons.

The prediction freezes `federal`, `sal-v4`, and docket Term 2025. The matching committed statpack table supplies the bracketed federal `reached` rates for every displayed strictly prior Term, 2017–2024. In ascending Term order, the rates and weighted denominators are 76.5%/17, 43.5%/23, 88.5%/26, 65.9%/41, 72.7%/11, 89.5%/19, 86.2%/29, and 60.0%/15. Their resolved-weighted pool is **132.039/181 = 0.7294972375690608**. The numerator is reconstructed from rounded displayed percentages, not an exact grant count. Basis: `risk_set`; skill: **1 - 0.0025 / 0.7294972375690608^2 = 0.9953022196677929**.

The caption renders all 10 of the pack's 10 Terms; the scored pool excludes 2025 and 2026. No version mismatch or truncated-table window applies. These figures describe the committed table available to this evaluation, not a freshly queried corpus: its header supplies no corpus-wide pull vintage, and no live corpus was consulted. This is one cell's baseline comparison, not a claim of general predictive performance.

## Reasoning quality: 0.62

The rationale identifies the central vehicle-specific consideration: the petition seeks a contingent hold-and-GVR, rather than independently developed plenary review, and the later opposition argues that the companion decision undermines the requested remand. It explains why the federal-petitioner average need not govern this particular petition and identifies the broader statutory issue as residual uncertainty.

Three weaknesses limit the score. First, its approximately 52% purported prior-Term anchor resembles the displayed own-Term rate, not the roughly 73% strictly-prior pool. Second, it groups Mitchell, Doucet, and Cockerham as post-Hemani denials even though the provisioned opposition dates Doucet to April 27 and Cockerham to June 8, before Hemani's June 18 decision; only Mitchell is dated afterward. Third, it treats the opposition's account as establishing that a GVR is no longer warranted, without distinguishing the companion statute from the statute here or exploring whether reconsideration could remain useful. The petition's own pages 3–4 frame the request around the intervening decision's effect on the lower court's analysis. The short rationale does not fully engage that uncertainty or justify the precise 5% estimate. The accurate outcome call does not erase these analytical shortcomings.

Only `reasoning.md` determines this qualitative score. The forecast document was read for context, not scored; structured quantitative claims remain the harness's responsibility. Cert votes and semantic claims are not scored.

## Leakage

The prediction and captured log both identify forward mode on September 16, before the recorded October 5 resolution. The visible queries read the provisioned snapshot, briefs, and statpack; the rationale does not reveal Hembree's own eventual disposition. Earlier companion-case material is legitimate forward context.

All 32 calls have `result_capture = unobserved` and coverage 0.0. That is a visibility limitation, not proof that their results were empty or a defect to penalize. On query scope, chronology, and prose, there is no affirmative evidence of an already-decided Hembree outcome entering the forecast: `retrieved_outcome_material = false`, influence `not_applicable`, and `leakage_suspected = false`.
