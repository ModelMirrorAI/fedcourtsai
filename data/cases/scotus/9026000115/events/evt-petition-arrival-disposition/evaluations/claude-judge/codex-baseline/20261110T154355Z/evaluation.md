# codex-baseline — evaluation

Cert-stage, arrival-moment, forward cell. Outcome: petition **denied** on 2026-11-09 (`actual_granted` 0) after a respondent waiver (Aug 25, 2026) and a single distribution for the 11/6/2026 conference; no CVSG, no relist, no noted dissent. The segment base rate, its basis and the skill score are the harness's to stamp; this write-up quotes no rate of its own. The claims block is scored in code and not graded here. No semantic set is declared on a cert cell.

## Score
- Predicted `denied` at P(grant) = 0.004 → `correct` = 1, `brier_score` = 0.000016.

## Reasoning quality — 0.82
A sound, specific analysis. It anchors on the baseline band's pooled rate from the statpack and adjusts down for petition-specific reasons that are well chosen and accurate on the record: no alleged circuit split, an unpublished one-paragraph CA4 per curiam, the district court's explicit application of *Groff v. DeJoy*, and an independent vehicle problem in the Rule 56(d) ruling (no affidavit, long discovery, delay). It also catches the petition's citation of 28 U.S.C. § 1257 for a federal court-of-appeals judgment as a presentation weakness. It discloses its failed retrievals candidly. The 0.004 is aggressive but well supported for this posture. Minor deduction: the § 1257 point is a weak signal, given extra weight in a short analysis.

## Predicted reasoning — 0.60
The central claims were: one distribution then denial at the first conference; no relist; no CVSG; no dissent or statement. All were borne out by the docket. They are specific, but they are the modal path for a fact-bound paid petition with no split, so a competent reader would rarely have called them otherwise. That puts the grade above generic but short of the top. The QP-narrowing content is conditional on a grant that did not happen and earns neither credit nor penalty.

## Leakage
Forward (predicted 2026-08-16, resolved 2026-11-09). The log shows provisioned-record reads, statpack reads, two corpus queries that never returned, and a rate-limited MCP search. Nothing post-resolution was retrieved. The final call's `[redacted:…]` markers are the credential scrub, not outcome material. `not_applicable`, not suspected.

## Big case
0.12. This is a fact-bound private Title VII accommodation dispute with no split.
