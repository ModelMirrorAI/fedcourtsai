# Evaluation of `claude-baseline` — `scotus/73280982` (`evt-brief-sg-disposition`)

## Outcome & Score Summary

On November 13, 2026, the Supreme Court granted certiorari limited to the Solicitor General's reformulated Question 1 for plenary review after two post-CVSG distributions (`distribution_count: 3`), with no separate writings (`actual_disposition: "granted"`, `actual_granted: 1`, `disposition_route: "plenary"`).

- **Categorical call (`correct = 0`):** Like `codex-baseline`, `claude-baseline` substantively anticipated a grant limited to Question 1 as reformulated by the Solicitor General, but coded `predicted_disposition: "granted-in-part"` rather than `"granted"`. Because the Court's order read `"Petition GRANTED limited to the following question: ..."` without `"in part"` phrasing, `outcome.json` recorded `actual_disposition: "granted"`, yielding `correct = 0` on exact-label matching.
- **Probabilistic call (`brier_score = 0.04`):** `probability = 0.80` against `actual_granted = 1`, substantially outperforming the stamped segment base rate.
- **Leakage (`leakage_suspected = false`):** Genuine forward forecast placed on October 26, 2026, eighteen days before the November 13, 2026 grant. All 12 logged calls were captured local shell inspections of `.github/prompts/predict.md`, `schemas/prediction.schema.json`, `metrics/statpack.md`, and the pre-cutoff October 7, 2026 provisioned files, with no external retrieval or `data/qp-topics/` reads.

## Reasoning Quality (`reasoning_quality = 0.81`)

Base-rate citations were checked against the statpack build in force when `claude-baseline` ran (`eb6830084a18`, digest `sha256:f6c3af155898c161beb3ba174781949a02784094085267d79a074680a859b1ba`), rather than the later committed `sal-v8` statpack.

**What drove the score upward:**
1. **Clean input verification and strictly-prior base-rate pooling:** `claude-baseline` caught that `questions-presented.txt` (at prediction time) held a body passage from the petition's importance argument rather than the Questions Presented, read the actual questions from `petition.txt`, accurately cited `eb6830084a18`'s CVSG cut (`n = 164` resolved: 29.3% `granted` + 5.5% `gvr`), and pooled the `sal-v4` `high` risk-set rows strictly over prior Terms 2017–2024 (`n = 898` weighted, properly excluding the case's own Term 2025).
2. **Transparent calibration and sensible secondary claims:** `claude-baseline` separated its background literature estimate for SG grant recommendations (~70–80%) from committed statpack tables, balanced upward factors (SEC co-signing, pure-law posture below, *Stadnick* and *Omnicare*/*Macquarie* tension, three cert amici, elite counsel) against downward vehicle concerns (partial recommendation with reformulation, respondents' non-adversity argument, interlocutory posture) to land on `0.80`, and produced coherent `cert-v2` secondary claims (`relist-increment: 0.96`, vacuous `cvsg-increment: 0.01`, `summary-disposition-route: 0.03`).

**Deductions:**
1. **Mis-mapped a limited-question SCOTUS cert grant to `granted-in-part`:** `claude-baseline` chose `predicted_disposition: "granted-in-part"` solely because the grant would be limited to Question 1, overlooking that SCOTUS `"Petition GRANTED limited to..."` orders map to `"granted"` in the pipeline's disposition taxonomy (consistent with `eb6830084a18`'s CVSG breakdown showing zero `granted-in-part` entries).
2. **Thinner doctrinal engagement with the party briefing:** Compared with a deeper synthesis of the BIO and cert reply, `claude-baseline`'s rationale is relatively terse on how respondents reconciled their concession that Section 11 requires misleadingness with the Ninth Circuit's categorical holding on interim metrics, and why the SG found that tension insufficient to defeat adversity once Question 1 was reformulated.

## Predicted Reasoning (`predicted_reasoning_quality = 0.88`)

`claude-baseline`'s `predicted_reasoning.md` was concise, well-focused, and borne out on all testable cert-stage commitments:

- **Grant limited to Question 1 in the SG's reformulated wording (`borne-out`):** Forecast certiorari granted limited to Question 1, `"likely as reformulated by the Solicitor General"` (quoting the `"without an additional inquiry"` formulation) with Question 2 denied or not reached — matching the November 13, 2026 order, though phrased slightly more tentatively (`"likely"` / `"most likely"`, naming a two-question grant as the main alternative) than an unqualified commitment.
- **November 2026 conference timing and relist path (`borne-out`):** Forecast redistribution for a November 2026 conference after supplemental briefs and a grant at the `"first or second post-CVSG conference"` (`"one relist before the grant is plausible but not the main path"`), which held when the Court granted at the second post-CVSG conference (November 13, 2026) after one relist (`distribution_count: 3`).
- **Plenary route (`borne-out`):** Correctly forecast plenary briefing and argument with no GVR, summary reversal, or further CVSG.
- **Separate-writing coverage and conditional merits ground:** Addressed separate writings only conditionally (`"If denied"`), omitting an explicit call on whether a separate statement would accompany the grant order itself, while its conditional merits forecast under *Omnicare* and *Macquarie* is `unresolved` on the cert-stage record.
