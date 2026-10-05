# Evaluation: gemini-baseline

## Outcome and quantitative scores

This cert-stage event resolved as `denied` on October 5, 2026, with `actual_granted = 0`. gemini-baseline predicted `denied` on September 17 with grant probability 0.01. Exact-label correctness is **1**; the Brier score is **0.0001**, or `(0.01 - 0)^2`. The recorded denial supplies no substantive explanation of the Court's reasoning.

The prediction froze Term 2025, band `baseline`, and version `sal-v4`. The committed statpack heading matches that version. The scored baseline uses the bracketed **reached** rates, not the terminal zero-relist rate discussed in the rationale, and records `base_rate_basis = risk_set`.

| Prior Term | Reached rate | Weighted resolved denominator |
| --- | ---: | ---: |
| 2024 | 5.7% | 1271 |
| 2023 | 5.9% | 1312 |
| 2022 | 5.8% | 1192 |
| 2021 | 5.6% | 1500 |
| 2020 | 4.5% | 1739 |
| 2019 | 4.6% | 1399 |
| 2018 | 4.6% | 1524 |
| 2017 | 4.7% | 1643 |

The weighted reconstruction is `592.925 / 11580 = 0.05120250431778929`; the fractional numerator comes from rounded printed rates and is not an integer observed grant count. Terms 2025 and 2026 are excluded. The table renders 10 of 10 Terms, and all eight strictly-prior displayed rows are included. There is no rendered-window omission. Brier skill is `1 - 0.0001 / 0.05120250431778929^2 = 0.961856758794282`. A favorable single-denial score is not a calibration result across cases.

These are the committed denial-reweighted live/historical rollup figures, without an independent remote-corpus freshness check. The evaluator's snapshot is dated October 5, and the candidate's frozen snapshot date is September 16, 2026; neither is represented as a corpus-wide newest-pull stamp.

## Reasoning quality: 0.58

The rationale recognizes the correct procedural posture and identifies plausible reasons for a low review probability: an unpublished state-court arbitration decision, a waived response, and no developed split in the supplied materials. It does not mistake one distribution for a completed relist sequence. Those points are directionally sound and consistent with the eventual denial, without establishing why the Court denied review.

Its main weakness is baseline interpretation. It acknowledges the prior-Term reached rates but then anchors near the terminal zero-relist bucket's 1.2% `granted` share. A petition at its first conference can later move into another bucket; the terminal bucket excludes that future path and is not the same risk-set population. Moreover, the displayed zero-relist row also contains 0.5% GVRs, which belong on the any-grant axis. The rationale does not explain either distinction. Its legal analysis is also thin: it does not address the petition's acknowledgment of the alternative federal-standard analysis, distinguish the neutrality theories, or explain the absence of an outcome-determinative conflict beyond a brief assertion. The 1% point estimate is plausible but only lightly justified.

This score grades `reasoning.md`, not its length as such, the separately staged forecast, or the structured auxiliary claims. The retrieval-report discrepancy below is not an additional reasoning-quality penalty.

## Leakage and reporting

The harness records `forward`. All 26 calls have `result_capture = unobserved`, giving capture coverage 0.0. This is a visibility limitation, not a failed-call finding or a tooling defect. The visible queries name the September 16 snapshot and provisioned documents. The prediction predates the October 5 denial, and the prose contains no indication that the eventual disposition was known.

One logged shell call attempts `uv run fedcourts query --court scotus --era 2020s --decided-before "2026-09-16" | grep -i arbitrat | head -n 10`. This is a general, date-bounded prior-case search, not a query for this petition's outcome. Its result is unobserved: I cannot infer that it succeeded, failed, or returned no rows. The staged `retrieval.md` says only "No retrieval beyond the provisioned inputs." That omits the attempted corpus lookup. A cell-level data-quality flag records this narrow reporting inconsistency; it does not allege outcome exposure.

On the visible queries, chronology, and reasoning, no outcome-revealing material is shown. I therefore record `retrieved_outcome_material = false`, influence `not_applicable`, and `leakage_suspected = false`, explicitly subject to the unobserved-result limitation rather than treating the null dates as evidence of clean results.

## Scope

The forecast document was read only for context. Cert-stage votes are unscored; there is no merits judgment or declared semantic set. No vote, judgment, semantic, or mechanical claim score is supplied. Harness-owned provenance and linkage fields are left unwritten.
