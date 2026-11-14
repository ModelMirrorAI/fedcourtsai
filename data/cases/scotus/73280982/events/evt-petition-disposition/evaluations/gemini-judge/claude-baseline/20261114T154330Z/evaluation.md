# Evaluation of `claude-baseline` — *Robinhood Markets, Inc. v. Sodha* (`scotus/73280982`, `evt-petition-disposition`)

## Quantitative Summary

- **Stage:** `cert` (`evt-petition-disposition`, resolved `2026-11-13`)
- **Outcome:** `actual_disposition = "granted"`, `actual_granted = 1`, `disposition_route = "plenary"`
- **Prediction:** `predicted_disposition = "granted-in-part"`, `probability = 0.72`
- **Exact-match accuracy (`correct`):** `0` (`"granted-in-part"` against `"granted"`)
- **Brier score (`brier_score`):** `(0.72 - 1)^2 = 0.0784`
- **Baseline & skill:** `segment_base_rate`, `brier_skill_score`, and `base_rate_basis` are left null for harness stamping against the stamped segment base rate.

## Reasoning Quality (`reasoning_quality = 0.72`)

`claude-baseline` got the substantive direction and probability broadly right (`P(grant) = 0.72`), anchored cleanly on the historical statpack, and focused immediately on the Solicitor General's invited brief, but two clear shortcomings held back `reasoning.md`:

1. **Base-rate grounding (`statpack-at` check):** Verified via `fedcourts statpack-at` against build `eb6830084a18` (`sha256:f6c3af155898c161beb3ba174781949a02784094085267d79a074680a859b1ba`), the statpack build in force at `20261026T092709Z` (`sal-v4`), every figure `claude-baseline` cited—the OT2017–OT2024 `high`-band rates, the unconditional paid CVSG grant/GVR figures, and the `relist_bucket = 1` rates—matches that build accurately. `claude-baseline` reasoned sensibly that an affirmative SG grant recommendation moves the probability well above the stamped segment base rate and the unconditional CVSG average.
2. **Cert disposition vocabulary error (`granted-in-part` vs. `granted`):** `claude-baseline` selected `predicted_disposition = "granted-in-part"` on the theory that "the SG recommends granting only Q1 (reformulated) and denying Q2." In this pipeline's SCOTUS cert vocabulary (immediately visible in `statpack.md`'s modern discretionary-cert disposition table, where `granted` has 662 rows, `gvr` has 588, and `granted-in-part` has 0), an order granting a certiorari petition limited to one question presented is coded `"granted"` (`disposition_route = "plenary"`), whereas `"granted-in-part"` reflects partial relief on motions or interim applications. That preventable schema misread cost `claude-baseline` exact-match accuracy (`correct = 0`).
3. **Partial engagement with provisioned party filings:** `reasoning.md` and `retrieval_log.json` show that `claude-baseline` read `sg-invited-brief.txt` and short `grep` excerpts of `brief-in-opposition.txt`, but never opened `petition.txt` (not even to inspect the actual Questions Presented pages after noting that `questions-presented.txt` contained a body excerpt) or `cert-reply.txt`. As a result, its evaluation of Respondents' Item 303 alternative-ground vehicle objection was cursory, and it slightly over-discounted for routine 12(b)(6) interlocutory posture and the unprovisioned October 20–21 supplemental briefs (`0.72`, yielding a Brier score of `0.0784`).

## Predicted reasoning (`predicted_reasoning_quality = 0.86`)

Evaluated strictly on `predicted_reasoning.md` (without re-penalizing `prediction.json`'s enum choice, which `correct` already scores), `claude-baseline`'s prose forecast held up well against the staged record:

- **Plenary grant limited to Question 1 as reformulated by the SG (`borne-out`):** `predicted_reasoning.md` led with *"Disposition: grant, most likely limited to Question 1 (as reformulated by the Solicitor General)"* and explicitly called *"Plenary review rather than summary disposition"* while predicting Question 2 (Item 303) would not be taken. On November 13, 2026, the Court entered a plenary grant limited verbatim to the Solicitor General's reformulated Question 1 and excluded Question 2.
- **One relist after the November 6, 2026 Conference (`borne-out`):** Forecast that one further distribution after the `11/6/2026` conference was slightly more likely than not before the grant order issued—citing the Court's routine practice of relisting once before granting, especially when reformulating a question presented—with no further CVSG. The docket shows a third distribution on `Nov 09 2026` for the `11/13/2026` conference (`outcome.signals.distribution_count = 3`) followed by the `Nov 13 2026` grant.
- **No separate cert-stage writings (`borne-out`):** Correctly forecast that no separate writings would accompany a grant order.
- **Expected merits ground (`unresolved`):** Its conditional merits call (vacatur or reversal on Question 1 under *Omnicare* without reaching Item 303) was not tested by the cert order and neither lifts nor lowers the grade.

All three resolved cert-stage commitments were discriminating and borne out; the grade sits at `0.86` (rather than `0.90+`) because the relist forecast was mildly hedged ("slightly more likely than not") and the prose stated the reformulated question's substance more compactly than the richest forecasts.

## Leakage & Retrieval Audit

- **Mode:** `forward` (`leakage_suspected = false`, `influenced_prediction = "not_applicable"`, `retrieved_outcome_material = false`).
- All 11 calls in `retrieval_log.json` (`result_capture_coverage = 1.0`) ran between `2026-10-26T09:32:34Z` and `2026-10-26T09:33:50Z`, eighteen days before the `2026-11-13` grant order, reading only provisioned local files and `metrics/statpack.md` with no external or corpus retrieval.

## Big-Case Stake Read (`evaluator_score = 0.60`)

Independently assessed from the case record and granted question, *Robinhood Markets v. Sodha* warrants `0.60`: clarifying whether materiality alone triggers strict Section 11(a) omission liability for intra-quarter financial metrics affects IPO registration statements and securities class actions nationwide (drawing SG/SEC, Chamber of Commerce, and SIFMA participation), while remaining a focused statutory capital-markets dispute rather than a constitutional or administrative-law blockbuster.
