# Evaluation: claude-baseline

## Outcome and quantitative scores

This is a cert-stage cell. The supplied outcome records denial on October 5, 2026, with `actual_granted = 0`. The candidate predicted `denied` with P(grant) = 0.004: exact-label correctness is **1** and Brier loss is **0.000016**.

The candidate's frozen context supplies Term 2025, band `baseline`, and version `sal-v4`; the committed `metrics/statpack.md` table names the same version. I use the bracketed reached population, not the terminal rate or this evaluator's context. The displayed strictly prior Terms are 2017–2024. Their reached rate/weighted-n pairs, newest first, are 5.7%/1271, 5.9%/1312, 5.8%/1192, 5.6%/1500, 4.5%/1739, 4.6%/1399, 4.6%/1524, and 4.7%/1643. Pooling the displayed rounded rates gives **0.05120250431778929** over weighted n = **11,580**, on a `risk_set` basis. Baseline loss is 0.0026216964484132308; skill is **0.9938970814070851**. This is a calculation from the committed denial-reweighted live/historical-slice table, not a fresh corpus census. The caption renders all 10 pack Terms; excluding 2025–2026 creates no table-window truncation. The rate is approximate because the displayed percentages are rounded.

## Reasoning quality: 0.80

The rationale identifies the relevant information set and uses the appropriate frozen-band prior. Its case-specific downward adjustment is coherently tied to the petition's individual grievances, undeveloped conflict assertion, response waivers, and lack of visible additional attention. It distinguishes a federal respondent from a federal petitioner and leaves a nonzero probability rather than claiming certainty. Those are strengths independently of the eventual denial.

The analysis nevertheless overstates some support. “No legal question” is broader than the defensible conclusion that the supplied text does not develop a cert-worthy conflict or general question. The document makes categorical assertions about prior denials and absence of Justice writings without establishing a comprehensive source for them. Its claimed pro-se rate differential is not quantified from an appropriate comparison population, and five selected grants, mostly applications, do not establish calibration for this cert petition. The supplied petition reports the decisions below; it is not a substitute for independently reading their reasoning. These limitations reduce the analytical grade without altering the mechanical score. The denial alone does not establish the Court's reasons or validate the exact 0.4% probability.

## Leakage and scope

The frozen context and harness log identify a forward prediction. The rationale describes a September 16 snapshot ending in distribution for the September 28 conference. The captured calls occurred September 17, before the recorded October 5 disposition, and contain no case-specific outcome retrieval. The corpus query sought unrelated grants; it is not evidence that this petition's outcome was known. Capture coverage is 1.0, although the staged log supplies digests rather than full result bodies. I find no outcome material shown and record `not_applicable`, with leakage not suspected.

Only `reasoning.md` determines reasoning quality. I read `predicted_reasoning.md` for context but did not grade it or the mechanical claims. Cert votes are unscored, no semantic set applies, and no independent big-case assessment is supplied. Harness-owned fields remain absent.
