# Evaluation — codex-baseline — scotus/9526000680, evt-motion-disposition

**Stage: interim** (stay application, arrival moment). Outcome: denied by Justice Sotomayor on 2026-11-13; `interim_reading` = denied, `interim_granted` = 0.

## Scores
- `correct` = 1: predicted `denied`, which sits on the ungranted side with `interim_granted` = 0.
- `brier_score` = (0.03 − 0)² = 0.0009.
- The baseline and skill (`segment_base_rate`, `brier_skill_score`) are the harness's on an interim cell; I wrote neither, and `base_rate_basis` stays null. The prediction froze no band, so no cert-band flag applies. No `vote_accuracy` and no `semantic_grades` on an interim cell.

## Reasoning quality — 0.80
Sound and well disciplined. It anchors on the scored interim pool, moves to the private/unmarked descriptive cell without treating it as the yardstick, and then explains the remaining cut by concrete vehicle problems: doubtful finality under § 1257 for an unfinished foreclosure (with a checked reading of the fourth *Cox Broadcasting* category rather than the applicant's gloss), a fact-bound dispute with no split, and broad requested relief against a hearing that is not itself a dispossession. It states the *Hollingsworth* standard correctly and is careful to label the application's account as allegation, to note that no appendix or opposition was provisioned, and to refuse to read the absence of a response request at arrival as an adverse act. Those are all correct calls on this record. The base-rate figures match the other candidates' and the pack; I had no reason to rebuild another build.

What keeps it from higher: the analysis stays on the application's face, so it does not find the strongest points against relief (the timeliness question around the June certification denial, the state appellate stay), and 3% is somewhat generous for a pro se interlocutory foreclosure stay — it does not separate that stream from counselled private applications inside the 7% cell. The fairness-to-the-applicant section is balanced but slightly over-weighted for a 3% call.

## Predicted reasoning — 0.70
Central claims: an unexplained denial by Justice Sotomayor; no response request, referral or amicus; no separate writing; action by about November 16. All four are borne out by `outcome.json` and the decided docket (denied Nov 13, signals all zero). The conditional ground for an explained denial is unresolved because the order gives no reasons, and earns neither credit nor penalty. The document is specific on route and actor, but it frames each rung as a probability rather than a flat commitment and adds a secondary timing window, and the path it called is the heavily modal one for this kind of application, so it sits just under the 0.75 anchor.

## Leakage
Mode forward. The event resolved on 2026-11-13 and this prediction was created on 2026-11-14, so the case was in fact already decided when the cell ran; the snapshot it was given (2026-11-12) held only the submission entry. I therefore checked the log rather than passing it by default. All 34 calls are local reads, one corpus citation query, and CourtListener lookups for two precedents; the two unobserved web-search rows carry general-precedent queries. Nothing targets this docket, no document date falls on or after the resolution, and the prose expects action "most likely by November 16". No outcome material surfaced: `influenced_prediction` = `not_applicable`, `leakage_suspected` = false. The timing itself is flagged in `flags.json`.

## Big case — 0.03
A single-property pro se foreclosure stay with no reach beyond the parties.
