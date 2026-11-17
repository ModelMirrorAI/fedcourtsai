# Evaluation of `gemini-baseline` (`scotus/9026000210` — `evt-petition-arrival-disposition`)

## Outcome and Quantitative Summary

- **Stage / Moment:** `cert` (`arrival`, forecast at docketing)
- **Predicted vs. Actual Disposition:** Predicted `granted` (`P(grant) = 0.85`); actual outcome was `denied` (`actual_granted = 0`, resolved `2026-11-16` on first conference with `distribution_count = 1`, `cvsg_date = null`, and `noted_dissent_from_denial = false`).
- **Accuracy & Brier Score:** `correct = 0`, `brier_score = 0.7225`. `segment_base_rate`, `base_rate_basis`, and `brier_skill_score` are left to the harness stamp against the stamped segment base rate.
- **Base-Rate Build Checked:** Evaluated against prediction-time statpack build `02dd6a20fccc` (`sha256:5b70d73d2cadac0dff2091d5aa32536fb116a3366f76592493006ca63337d0cc`, `sal-v3`), reconstructed via `fedcourts statpack-at` (distinct from the later committed `sal-v8` statpack).

## Reasoning Quality (`reasoning_quality = 0.38`)

`gemini-baseline`'s `reasoning.md` correctly identified the core structural reason to assign a substantial prior grant probability — the Solicitor General petitioned on behalf of the United States (`band: federal`) to overturn an appellate decision affirming a preliminary injunction against major presidential executive orders — and recognized in passing that the case's preliminary-injunction posture was a plausible reason review could be denied. However, the analysis in `reasoning.md` is thin, skips reading the petition itself, and misses nearly every doctrinal and procedural feature that pointed away from pushing `P(grant)` up to `0.85`:

1. **Imprecise base-rate anchoring:** Rather than pooling the strictly prior Term rows of the `sal-v3` `federal` risk-set table in build `02dd6a20fccc`, `gemini-baseline` gestured loosely to a broad range and immediately adjusted upward to `0.85` without checking recent-Term behavior or justifying the magnitude of the upward move beyond generic executive-action salience.
2. **Misstatement of the Ninth Circuit's holding on the Form Termination Class:** `gemini-baseline` wrote that "the Form Termination Class lacked standing/APA success." In fact, the Ninth Circuit expressly *upheld* Article III standing for all plaintiffs (`App. 8a–10a`) and reversed as to the Form Termination Class specifically because the **Tucker Act** (`28 U.S.C. § 1491(a)(1)`) and *NIH v. American Public Health Ass'n*, 145 S. Ct. 2658 (2025), stripped the district court of jurisdiction over the APA grant-termination claims (`App. 11a–15a`). Because `gemini-baseline` did not read `petition.txt` and read only the opening chunk of the Ninth Circuit opinion via MCP, it missed both the actual ground of partial reversal and the resulting Tucker Act / third-party privity vehicle complication hovering over the First Amendment grant-reinstatement injunction (which the Solicitor General spent pages 23–24 of the petition trying to explain away as non-jurisdictional and forfeitable).
3. **Zero engagement with precedent or percolation:** `reasoning.md` cites not a single Supreme Court precedent — omitting *Rust v. Sullivan*, *NEA v. Finley*, *Rosenberger*, and *USAID* entirely — and never mentions the complete absence of a circuit split or the dozen-plus parallel grant-termination suits actively percolating across the First, Second, Fourth, Seventh, Ninth, and D.C. Circuits (catalogued in the petition itself, including an overlapping permanent nationwide class injunction on appeal in the Second Circuit). It also treats the interlocutory preliminary-injunction posture only as a parenthetical afterthought in its dissent-from-denial sentence rather than weighing posture, percolation, or unreached statutory alternative grounds (`App. 15a`) in its cert probability.

## Predicted reasoning (`predicted_reasoning_quality = 0.08`)

`gemini-baseline`'s `predicted_reasoning.md` committed to a confident grant narrative and missed every non-trivial testable claim resolved by the staged record:

- **Central claim 1 — Certiorari grant (`not-borne-out`):** The document's headline forecast ("I expect the petition to be granted. The Court is highly likely to take up this case...") failed when the Court denied certiorari (`actual_disposition: "denied"`).
- **Central claim 2 — One or two relists prior to disposition (`not-borne-out`):** The document forecast "one or two relists before a decision on the petition" (hedging that a first-conference grant was possible). Instead, the petition was distributed once on October 28, 2026 for the November 13, 2026 conference (`distribution_count: 1`) and denied on November 16, 2026 with zero relists.
- **Central claim 3 — No CVSG (`borne-out`, minimal discriminating weight):** Calling no CVSG held (`cvsg_date: null`), but is virtually entailed by the Solicitor General appearing as counsel for petitioners.
- **Central claim 4 — Conditional scope and plenary review (`unresolved`):** Taking the QP as written for full briefing and oral argument rather than summary reversal was conditioned on a grant that never occurred, earning neither credit nor penalty.
- **Central claim 5 — Noted dissent from denial if denied (`not-borne-out`):** Crucially, the contingent branch for denial *was* tested by the outcome, and `gemini-baseline` affirmatively forecast that "[s]hould the Court deny the petition, expect a dissent from denial from several of the conservative justices." The Court denied the petition cleanly with no noted dissents or statements (`noted_dissent_from_denial: false`).

With the central disposition claim wrong in direction, the relist forecast wrong, and the tested conditional-on-denial dissent forecast also wrong, the document sits just above the `0.0` anchor solely for its accurate (though routine) no-CVSG call.

## Leakage Assessment

- **Mode:** `forward` (`leakage_suspected = false`, `influenced_prediction = "not_applicable"`, `retrieved_outcome_material = false`).
- The prediction ran on `2026-08-20`, one day after docketing (`2026-08-19`) and almost three months before the `2026-11-16` cert denial. Although all 21 logged calls record `result_capture: "unobserved"`, the logged queries inspect only provisioned case metadata, `metrics/statpack.md`, a pre-cutoff Ninth Circuit corpus query, and the published May 2026 Ninth Circuit opinion below on CourtListener (`opinion_id: 11331917`), with no `data/qp-topics/` reads or outcome leakage.
