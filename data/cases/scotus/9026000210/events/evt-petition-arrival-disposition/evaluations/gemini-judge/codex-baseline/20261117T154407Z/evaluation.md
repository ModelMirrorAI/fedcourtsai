# Evaluation of `codex-baseline` (`scotus/9026000210` — `evt-petition-arrival-disposition`)

## Outcome and Quantitative Summary

- **Stage / Moment:** `cert` (`arrival`, forecast at docketing)
- **Predicted vs. Actual Disposition:** Predicted `granted` (`P(grant) = 0.78`); actual outcome was `denied` (`actual_granted = 0`, resolved `2026-11-16` on first conference with `distribution_count = 1`, `cvsg_date = null`, and `noted_dissent_from_denial = false`).
- **Accuracy & Brier Score:** `correct = 0`, `brier_score = 0.6084`. `segment_base_rate`, `base_rate_basis`, and `brier_skill_score` are left to the harness stamp against the stamped segment base rate.
- **Base-Rate Build Checked:** Evaluated against prediction-time statpack build `02dd6a20fccc` (`sha256:5b70d73d2cadac0dff2091d5aa32536fb116a3366f76592493006ca63337d0cc`, `sal-v3`), reconstructed via `fedcourts statpack-at` (distinct from the later committed `sal-v8` statpack).

## Reasoning Quality (`reasoning_quality = 0.74`)

`codex-baseline`'s `reasoning.md` is a disciplined, well-structured arrival-stage analysis that achieved the best calibration of the cohort (`0.78`), though it still overpredicted grant probability by adjusting upward rather than downward from the `federal`-band anchor.

**What drove the grade upward:**
1. **Exact base-rate methodology:** Checked against prediction-time statpack build `02dd6a20fccc` (`sal-v3`), `codex-baseline` selected the right arrival-time population (`band: federal` risk set across the nine displayed prior Terms strictly preceding OT2026), pooled the exact weighted counts from that build without arithmetic error, and clearly explained why neither the overall paid-cert rate nor the terminal `relist_bucket = 0` cut represents the arrival-stage risk set.
2. **Thorough record verification and epistemic discipline:** `codex-baseline` read the full petition argument and appended Ninth Circuit decision (accurately noting where `petition.txt`'s 155-page extraction ended inside the district-court order) and highlighted the single biggest informational limitation at `moment: arrival`: no Brief in Opposition had yet been filed to surface respondents' vehicle and remedial objections.
3. **Accurate diagnosis of the countervailing cert risks:** `codex-baseline` explicitly identified the three structural vulnerabilities that ultimately aligned with a first-conference denial: (a) the absence of a developed circuit split, (b) the interlocutory preliminary-injunction posture, and (c) potential jurisdictional, remedial, class, or mootness complications.

**What held the grade back:**
1. **Upward net adjustment despite severe percolation and vehicle headwinds:** Having correctly identified the lack of a circuit split, the preliminary-injunction posture, and the missing BIO, `codex-baseline` nevertheless adjusted *upward* above the `sal-v3` `federal` anchor rather than discounting below it.
2. **Under-specification of the concrete vehicle tangles already visible in the petition:** While `codex-baseline` flagged "jurisdictional, remedial, class, or mootness developments" in general terms, the petition and Ninth Circuit opinion already exposed specific obstacles: (a) active, simultaneous percolation across half a dozen circuits — including an overlapping *permanent* nationwide class injunction against NEH grant terminations already on appeal in the Second Circuit (*ACLS v. NEH*, Pet. 22), which reduced the urgency of reviewing a UC-only preliminary injunction first; (b) the unresolved tension between *NIH v. APHA*, 145 S. Ct. 2658 (2025) (which the Ninth Circuit held barred APA grant-reinstatement jurisdiction for the Form Termination Class) and the SG's forfeiture/non-jurisdictional theory on the First Amendment claim (Pet. 23–24); and (c) the Ninth Circuit's decision not to reach respondents' statutory alternative grounds (`App. 15a`), as well as recent-Term dilution in the `sal-v3` `federal` band across OT2024–OT2025.

## Predicted reasoning (`predicted_reasoning_quality = 0.24`)

`codex-baseline`'s `predicted_reasoning.md` missed its central disposition call, placing it near the `0.25` rubric anchor ("A central claim failed, with the rest generic or mixed"), where its accurate secondary calls on conference timing and a silent denial keep it solidly at `0.24`:

- **Central claim 1 — Plenary grant (`not-borne-out`):** The headline commitment ("The Court will grant the petition and set the case for plenary briefing and argument") failed when certiorari was denied (`actual_disposition: "denied"`).
- **Central claim 2 — Late-2026 conference distribution without CVSG (`borne-out`):** `codex-baseline` forecast at least one distribution "most likely for a late-2026 conference," hedged relists appropriately ("may be held for one additional conference"), and called no CVSG. The petition was distributed once on October 28, 2026 for the November 13, 2026 conference (`distribution_count: 1`, `cvsg_date: null`) and resolved from that conference.
- **Central claim 3 — Conditional grant scope and plenary vs. summary route (`unresolved`):** Taking the QP substantially as written for plenary review rather than summary reversal or GVR was conditioned on a grant that did not occur.
- **Central claim 4 — No separate writing if denied (`borne-out`):** Because review *was* denied, `codex-baseline`'s contingent denial call ("If review is denied, no separate writing is the likeliest outcome") was directly tested and borne out (`noted_dissent_from_denial: false`, clean `"Petition DENIED."` order).
- **Central claim 5 — Conditional merits holding (`unresolved`):** The forecast merits rule under *Rust* and *Finley* was conditioned on plenary review and never tested.

## Leakage Assessment

- **Mode:** `forward` (`leakage_suspected = false`, `influenced_prediction = "not_applicable"`, `retrieved_outcome_material = false`).
- Executed on `2026-08-20` with 100% captured tool-call telemetry (`result_capture_coverage: 1.0`) while the case was newly docketed and unresolved. Every call read only workspace prompt/schema files, the provisioned arrival record, and `metrics/statpack.md`, with no external lookups or `data/qp-topics/` access.
