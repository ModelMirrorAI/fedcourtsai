# Evaluation of `claude-baseline` — *Eric Alan Isaacson v. Maribel Moses, et al.* (`scotus/73522552`, `evt-order-call-for-response-disposition`)

## Outcome and quantitative summary

- **Actual outcome**: `denied` (`actual_granted: 0`, `resolved_at: "2026-11-09"`, `noted_dissent_from_denial: false`, `signals.distribution_count: 2`, `signals.cvsg_date: null`).
- **Predicted disposition**: `denied` (`granted: 0`, `probability: 0.06`, `confidence: 0.85`).
- **Accuracy (`correct`)**: `1`.
- **Brier score**: `(0.06 - 0)^2 = 0.0036`.
- **Baseline and skill**: `segment_base_rate`, `base_rate_basis`, and `brier_skill_score` are left null for harness stamping against the stamped segment base rate.
- **Statpack build graded against for base-rate use**: Reconstructed via `uv run fedcourts statpack-at` for `run_id: "20261029T142045Z"` as commit `7bcde3b105cb212283905eda17b827efc188e80c` (`sha256:84feb6798b6407fea2a17fed92c36d8a8db71d12850a967d840f018295ba4641`, `sal-v4`), which was in force when the candidate ran (as distinct from the currently committed `sal-v8` statpack).

## Reasoning quality (`reasoning_quality: 0.84`)

`claude-baseline`'s `reasoning.md` is concise, well-grounded in both the provisioned case record and the reconstructed `sal-v4` statpack build (`7bcde3b105cb`), epistemically transparent, and well-calibrated:

1. **Accurate record grounding**: `claude-baseline` accurately reported every key fact from `2026-08-20.json` and `petition.txt`: the June 18, 2026 filing date; the July waivers by both respondents (Maribel Moses and The New York Times Co.); the August 5, 2026 distribution for the September 28 conference; the August 19, 2026 Call for a Response; the February 10, 2026 Second Circuit summary order (and March 20, 2026 rehearing denial) affirming the $5,000 service award in a $2.375M class settlement over the objection of pro se lawyer/objector Eric Alan Isaacson; and the 5–1 circuit split between the Eleventh Circuit (*Johnson v. NPAS Solutions*, 2020; en banc denied 2022) and the First, Second, Seventh, Ninth, and Federal Circuits (including the 2026 Federal Circuit decision in *NVLSP v. United States*). It also noticed the Chamber of Commerce entry under `"Other"` in the snapshot's party block and noted that no amicus entry appeared in the cut proceedings as of August 20, 2026.
2. **Accurate base-rate anchoring (`7bcde3b105cb`, `sal-v4`)**: `claude-baseline` read the `Segment base rate by salience band (sal-v4)` table in `metrics/statpack.md`, accurately cited the `baseline` bracketed `reached` rates across Terms `2017–2024` from the build in force when it ran, and noted that no committed statpack table conditions on a called-for response.
3. **Disciplined calibration and epistemic transparency**: `claude-baseline` articulated a sensible general lift from a Call for a Response on a paid baseline petition (`~8–12%`), then offset it downward for two specific reasons: (a) the Court's repeated denials of petitions raising the same *Greenough*/*Pettus* split since 2020—which `claude-baseline` explicitly labeled as unverified recall rather than attributing it to non-existent pages of the petition—and (b) the weak vehicle (a $5,000 award, an unpublished summary order, and a self-represented objector where the CFR likely served only to ensure adversarial briefing before denial). The resulting `0.06` probability (sitting just above the stamped segment base rate) coheres tightly with the prose. The only minor limitation is that `claude-baseline` did not use CourtListener or web search to verify its recall of the prior cert denials or read the full *Moses I*/*Moses II* appendix text beyond the opening 15 KB and targeted grep excerpts.

## Predicted reasoning

Evaluated strictly against the resolved record (`outcome.json` and `2026-11-09.json`), `claude-baseline`'s `predicted_reasoning.md` (`predicted_reasoning_quality: 0.78`) was crisp and accurate on every unconditional claim while keeping its grant/authorship contingencies explicitly conditional:

- **Disposition and timing (`borne-out`)**: Forecast that the Court would deny the petition at the first conference after the response and reply were distributed (`actual_disposition: "denied"` on Nov. 9, 2026, immediately following the Nov. 6, 2026 conference).
- **Distributions (`borne-out`)**: Forecast that the petition would come off the September 28, 2026 conference after the August 19 response request, be distributed once more once the response was filed (`relist-increment: 0.95`), and be decided at that first post-response conference with no further relist (`signals.distribution_count: 2`).
- **CVSG (`borne-out`)**: Forecast no CVSG (`cvsg-increment: 0.02`; `signals.cvsg_date: null`).
- **Conditional grant scope and route (`unresolved`)**: Properly kept its discussion of the single question presented (or a Rule 23(e)(2) rephrasing) and plenary-versus-summary review (`summary-disposition-route: 0.05`) conditional on a grant.
- **Separate writing on denial (`borne-out`)**: Forecast most likely no separate writing on denial (`dissent-from-denial: 0.05`), with Justice Thomas or Gorsuch likeliest if anyone wrote (`noted_dissent_from_denial: false`, `writing_roles: null`).

With every unconditional claim specific and borne out and conditional sections cleanly framed, `predicted_reasoning.md` earns `0.78`.

## Leakage and big-case read

- **Leakage (`not_applicable`, `leakage_suspected: false`)**: Forward prediction placed on October 29, 2026, eleven days before the November 9, 2026 denial. `retrieval_log.json` shows a single corpus query for 2020s SCOTUS granted priors (`--limit 5`) and no external lookups.
- **Big-case assessment (`evaluator_score: 0.35`)**: Forming an independent read of the case's stakes, a categorical Supreme Court ruling on *Greenough*/*Pettus* and Rule 23 service awards would affect federal class-action settlement practice nationwide, though this specific vehicle involves a $5,000 award in private consumer litigation affirmed by summary order and ended in an unremarked cert denial.
