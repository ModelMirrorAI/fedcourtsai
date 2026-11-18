# Evaluation of `claude-baseline` — `scotus/9026000369` (`evt-petition-disposition`)

## Quantitative Summary

- **Stage / Moment:** `cert` / `distribution`
- **Predicted vs. Actual Disposition:** `denied` vs. `denied` (`correct = 1`)
- **Probability / Brier Score:** `P(granted) = 0.02` vs. `actual_granted = 0` (`brier_score = 0.0004`)
- **Baseline & Skill:** `segment_base_rate`, `brier_skill_score`, and `base_rate_basis` are left for the harness to stamp from the committed statpack; `claude-baseline`'s `0.02` probability comfortably beats the stamped segment base rate on this denial.

## Reasoning Assessment (`reasoning_quality = 0.62`)

`claude-baseline` reached the right outcome call (`denied`, `0.02`) and correctly anchored on the frozen `baseline` context while discounting the marginal `2+` amicus statpack slice (verified against reconstructed statpack build `648fc43559f5` via `uv run fedcourts statpack-at`, where `18.2%` on `n = 1,446` for `2+` and `2.0%` for `0` match exactly). It also rightly flagged the unpublished three-paragraph Ninth Circuit memorandum (`App-1` to `App-2`), the two respondent waivers without a call for response, and the September 1, 2025 expiration of the restraining order (`App-3`).

However, `reasoning.md` exhibits significant analytical shortcuts that materially weaken its legal analysis:

1. **Incomplete inspection of the provisioned filings:** Although `reasoning.md` states *"Inputs read: snapshot `2026-10-31.json`, `context.json`, `same-question.json`, and the provisioned petition, QP and appendix texts"*, `retrieval_log.json` (`805ea009df300cc7`) shows `claude-baseline` read only the first 5,000 bytes of `appendix.txt` (stopping in `App-4`) and ran only a 40-line `grep` for `split|circuit|conflict` on `petition.txt` alongside reading `summaries/2026-10-23.md`.
2. **Speculating about holdings explicitly present in `appendix.txt`:** Because it stopped reading `appendix.txt` at `App-4`, `claude-baseline` wrote that the district court dismissed on multiple grounds that *"likely include immunity and failure to state a claim as well as Rooker-Feldman."* Pages `App-6` through `App-8` of the provisioned appendix explicitly set out those exact holdings—including Judge Evanson's quotation of Loop's operative complaint asking the district court *"to review the Washington State decision"* (`App-6`) and explicit Rule 12(b)(6) dismissals under absolute judicial immunity (*In re Castillo*) and arbitral immunity (*Sacks v. Dietrich*, `App-7` to `App-8`). Guessing at holdings that were two pages further down in a 571-line provisioned file is an avoidable analytical lapse.
3. **Omission of *T. M. v. University of Maryland Medical System Corp.* (June 18, 2026):** Because it skimmed `petition.txt` via `grep` and performed no CourtListener lookups, `claude-baseline` completely missed the Supreme Court's June 2026 decision in *T. M.*—cited in the petition itself—which reaffirmed *Rooker-Feldman* against a due-process suit seeking to invalidate and enjoin a state order while state appeals remained pending. Missing both *T. M.* and the literal de facto appeal language quoted at `App-6` also contributed to `claude-baseline` overstating the likelihood of a call for response and redistribution (`relist-increment = 0.25`).

## Predicted reasoning (`predicted_reasoning_quality = 0.76`)

`claude-baseline`'s `predicted_reasoning.md` concisely and accurately called the realized procedural outcome on the testable axes, though with notable hedging on conference trajectory:

- **Central claims borne out:** `claude-baseline` specifically named denial on the **November 16, 2026** order list following the November 13 conference (`resolved_at = 2026-11-16`, `actual_disposition = "denied"`), no CVSG (`cvsg_date = null`), and no dissent from denial (`noted_dissent_from_denial = false`). On conference trajectory, its modal call of immediate denial without further distribution held (`distribution_count = 1`), though it hedged substantially by calling a response request / redistribution *"the main uncertainty"* at `~25%`.
- **Conditional claims unresolved:** Its conditional grant claims (limiting review to QP 1 and a ~12% conditional chance of a per curiam vacatur faulting the Ninth Circuit's `"inextricably intertwined"` phrasing under *Exxon*) were never tested given the denial. Overall, naming the exact November 16 order-list denial and clean order earns a solid grade above the generic midpoint, tempered by the heavy 25% hedge on redistribution (`0.76`).

## Leakage & Big-Case Notes

- **Leakage (`not_applicable`, `leakage_suspected = false`):** Forward run executed `2026-10-31`, sixteen days before resolution, with 100% captured tool results in `retrieval_log.json`; no access to `data/qp-topics/` and no outcome-revealing material.
- **Big-case read (`0.10`):** Independent evaluator assessment reflects low systemic stakes for a vehicle-impaired *pro se* § 1983 collateral attack on an expired marital-dissolution restraining order summarily denied on waivers.
