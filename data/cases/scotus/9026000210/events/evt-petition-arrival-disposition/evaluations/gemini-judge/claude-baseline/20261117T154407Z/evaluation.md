# Evaluation of `claude-baseline` (`scotus/9026000210` — `evt-petition-arrival-disposition`)

## Outcome and Quantitative Summary

- **Stage / Moment:** `cert` (`arrival`, forecast at docketing)
- **Predicted vs. Actual Disposition:** Predicted `granted` (`P(grant) = 0.80`); actual outcome was `denied` (`actual_granted = 0`, resolved `2026-11-16` on first conference with `distribution_count = 1`, `cvsg_date = null`, and `noted_dissent_from_denial = false`).
- **Accuracy & Brier Score:** `correct = 0`, `brier_score = 0.64`. `segment_base_rate`, `base_rate_basis`, and `brier_skill_score` are left to the harness stamp against the stamped segment base rate.
- **Base-Rate Build Checked:** Evaluated against prediction-time statpack build `02dd6a20fccc` (`sha256:5b70d73d2cadac0dff2091d5aa32536fb116a3366f76592493006ca63337d0cc`, `sal-v3`), reconstructed via `fedcourts statpack-at` (distinct from the later committed `sal-v8` statpack).

## Reasoning Quality (`reasoning_quality = 0.73`)

`claude-baseline`'s `reasoning.md` combines rigorous base-rate work with the sharpest doctrinal diagnosis in the cohort of both the 2025 emergency-docket grant-termination stays and the lurking Tucker Act problem, but misfires on how active multi-circuit percolation and recent-Term `federal`-band dilution cut on `P(grant)`.

**What drove the grade upward:**
1. **Strong base-rate pooling plus recent-Term dilution insight:** Verified against prediction-time statpack build `02dd6a20fccc` (`sal-v3`), `claude-baseline` accurately pooled the strictly prior OT2017–OT2025 `federal` `reached` risk-set rows, rejected the terminal `relist_bucket = 0` cut and overall docket rate for the right reasons, and spotted a crucial feature inside the per-Term `sal-v3` table: the two most recent complete Terms (OT2024 and OT2025) ran substantially below the nine-Term average as Solicitor General petition volume rose.
2. **Specific doctrinal engagement with *NIH v. APHA* and the Tucker Act:** Unlike `gemini-baseline` (which misread the Form Termination Class ruling) and even more specifically than `codex-baseline`, `claude-baseline` connected this petition directly to *Department of Education v. California*, 604 U.S. 650 (2025), and *NIH v. APHA*, 145 S. Ct. 2658 (2025), noting that the Solicitor General deliberately refrained from pressing Tucker Act preclusion on the First Amendment claim below and that several Justices' preference for Tucker Act channeling could complicate this vehicle or prompt awaiting a cleaner case.
3. **Clear grasp of the litigation landscape:** `claude-baseline` identified the interlocutory preliminary-injunction posture and specifically noted the overlapping permanent nationwide class injunction entered in S.D.N.Y. with Second Circuit appeals pending (*ACLS v. NEH*).

**What held the grade back:**
1. **Inverted inference on active percolation:** Having observed that a dozen-plus parallel suits were pending across five or more circuits — including a *permanent* nationwide class injunction on overlapping grants already on appeal in the Second Circuit — `claude-baseline` treated active percolation as an *upward* lever ("Percolation is happening *now*, which cuts toward taking the first clean vehicle rather than waiting"). With zero circuit conflict yet in existence and final-judgment appeals underway in sister circuits, active percolation cut strongly *toward* denying this interlocutory single-university preliminary injunction rather than rushing ahead of the other circuits.
2. **Tension between diagnosing recent-Term SG dilution and adjusting upward to `0.80`:** After astutely observing that OT2024–OT2025 `federal`-band grant rates had fallen well below the nine-Term pool due to higher SG filing volume, `claude-baseline` nevertheless pushed its forecast significantly *above* the nine-Term pool to `0.80`, underweighting both that recent regime shift and the absence of a Brief in Opposition at `moment: arrival` (as well as the unreached statutory alternative grounds noted at `App. 15a`).

## Predicted reasoning (`predicted_reasoning_quality = 0.22`)

`claude-baseline`'s `predicted_reasoning.md` offered specific, concrete predictions rather than hedged generalities, but its headline grant call and its explicit relist call both failed, placing it just below the `0.25` anchor despite an impressive hit on briefing/conference timing and a sound contingent view of a silent denial:

- **Central claim 1 — Certiorari grant for plenary review (`not-borne-out`):** The document's central thesis ("The Court grants certiorari and sets the case for plenary briefing and argument" around December 2026–January 2027) failed when certiorari was denied on November 16, 2026 (`actual_disposition: "denied"`).
- **Central claim 2 — BIO extension pushing first distribution to a November/December conference, with no CVSG (`borne-out`):** From the August 20 docketing snapshot, `claude-baseline` specifically predicted that respondents would take an extension, pushing first distribution to a November or December conference. That discriminating procedural call held cleanly: respondents took a 30-day extension to October 19, 2026, pushing first distribution to October 28, 2026 for the November 13, 2026 conference (`cvsg_date: null`).
- **Central claim 3 — One to two relists beyond first distribution (`not-borne-out`):** `claude-baseline` affirmatively committed to "Expect one to two relists beyond the first distribution," reasoning that the lurking Tucker Act issue might prompt a second look. Instead, the Court denied certiorari immediately after its first conference (`distribution_count: 1`, zero relists).
- **Central claim 4 — Contingent silent denial (~70% no separate writing on a posture/percolation denial) (`borne-out`):** Conditional on denial, `claude-baseline` placed a noted dissent or statement at ~30% and explained that a vehicular/posture denial could well pass in silence. The denial order carried no noted dissent or statement (`noted_dissent_from_denial: false`; the unelaborated `"Petition DENIED."` order states no reasons).
- **Central claim 5 — Conditional grant scope, plenary route, and *Rust*–*Finley*–*USAID* merits ground (`unresolved`):** All grant-stage and merits-stage claims were explicitly conditional on certiorari being granted and were never tested by the record.

## Leakage Assessment

- **Mode:** `forward` (`leakage_suspected = false`, `influenced_prediction = "not_applicable"`, `retrieved_outcome_material = false`).
- Executed on `2026-08-20` with 100% captured tool-call telemetry (`result_capture_coverage: 1.0`) while the case was newly docketed and unresolved. Calls consisted solely of reading prompt/schema files, the provisioned arrival record, `metrics/statpack.md`, and a single `fedcourts query` by citation for *Rust v. Sullivan* (`500 U.S. 173`) that returned zero rows and was transparently logged, with no `data/qp-topics/` reads or post-resolution material.
