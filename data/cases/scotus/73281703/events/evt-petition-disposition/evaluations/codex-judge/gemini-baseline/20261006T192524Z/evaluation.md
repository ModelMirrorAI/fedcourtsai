# Evaluation: gemini-baseline

## Outcome and numerical scores

The cert-stage event resolved on October 5, 2026. The supplied `outcome.json` records `denied` and `actual_granted = 0`; the evaluator's October 5 snapshot also records the denial. gemini-baseline predicted `denied` with P(any grant) = 0.11, so exact-label correctness is **1** and Brier loss is **0.0121** = (0.11 - 0)^2. These scores concern the disposition, not whether the Court adopted the candidate's explanation.

The prediction froze Term **2025**, band **elevated**, and version **sal-v4**. That version matches the committed statpack heading. The risk-set baseline pools the bracketed elevated `reached` rates, resolved-weighted, across every displayed Term strictly before 2025: 2024 (17.9%, n=336), 2023 (17.5%, n=354), 2022 (19.0%, n=300), 2021 (20.5%, n=342), 2020 (16.1%, n=397), 2019 (13.8%, n=334), 2018 (15.9%, n=347), and 2017 (17.5%, n=400). The executed calculation gives **0.172379359430605**, weighted n = **2,810**. These are denial-reweighted estimates calculated from rounded displayed percentages, not raw case counts. The caption renders 10 of 10 Terms; excluding 2025 and 2026 leaves eight eligible rows, without a rendered-window discrepancy. The evaluator's terminal context does not determine this band.

The baseline's realized loss is approximately 0.02971464356; **Brier skill = 0.59279336545**. gemini-baseline beats this baseline on this denial. One result does not establish general calibration or forecasting skill. These figures describe the committed pack consulted, not a refreshed corpus census; no corpus lookup or claim of current corpus freshness is made.

## Reasoning quality: 0.58

The rationale makes a defensible denial call, starts near the relevant band rate, and recognizes that a requested response followed by redistribution need not mean repeated substantive relists. It identifies vehicle fit as the central counterweight to an important statutory question and acknowledges uncertainty about the response request's strength.

The principal weakness is analytical precision. The brief in opposition, printed pages 11-14, distinguishes an independent-contractor discrimination question from a nonemployee parent's retaliation claim and raises an antecedent private-action issue. The candidate mentions a mismatch only generically. Its discussion of possible independent state grounds also does not separate the ACRA and section 1983 claims from the section 504 claim. The opposition's pages 15-16 describe separate theories and a general verdict; merely accepting that presentation does not establish that no federal relief could follow reversal. gemini-baseline does not test this important premise against the competing account or explain the actual split in meaningful detail. Its approximate 17.5% anchor lacks the explicit prior-Term pooling supplied here, and the adjustment to 11% is weakly developed.

The lower Brier loss earns no automatic increase in reasoning quality. The supplied denial identifies no rationale and cannot confirm that vehicle defects, independent grounds, or any other particular consideration caused the Court's action. The score grades the substantive analysis in `reasoning.md` only. The pointed-to forecast was read for context; neither that document nor the quantitative claims are graded here.

## Leakage and scope

The stamped prediction context and captured log both say **forward**. The September 18 prediction and logged activity preceded the October 5 resolution. The 28 logged calls concern local inputs and output operations; the brief reads requested only their opening portions. No external case-outcome query or reasoning presupposing a disposition appears. The retrieval note reports no retrieval beyond provisioned inputs.

Result-capture coverage is **0.0**, with every call marked `unobserved`. Missing result dates and digests therefore do not prove that reads were empty or unsuccessful. On the available query scopes, timing, and prose, there is no affirmative evidence that this case's disposition surfaced early: `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`. The evaluator's later snapshot is not treated as the candidate's information set.

No cert vote accuracy or semantic grades are assigned. Mechanical claim scores and harness provenance fields are left to the harness. No blocking input defect, baseline-version mismatch, or likely leakage finding requires a flag.
