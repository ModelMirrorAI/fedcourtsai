# Evaluation of claude-baseline — scotus/9526000275, evt-motion-disposition

**Cell shape.** This is an **interim** cell (`event.yaml` `stage: interim`): an
emergency application for an injunction pending appeal, submitted to Justice
Kavanaugh 2026-08-31 and denied by the Circuit Justice 2026-09-03
(`actual_disposition: denied`, `actual_granted: 0`; signals: response
requested, not referred, zero amici at the order). Per the interim rules the
baseline and skill are the harness's: `stamp-cell` pools the statpack's
substantive-application grant rate over application-Terms strictly before
OT2026 and writes `segment_base_rate` and `brier_skill_score` itself. I write
neither and leave `base_rate_basis` null. For the reader: the committed pack's
strictly-prior rows are OT2025 (226 resolved / 17 granted) and OT2024 (70 / 14),
a pool of 296 that clears the registered floor of 50, so a non-null stamp is
expected; the harness's number governs, not any figure here. `claim_scores` is
likewise the harness's (`interim-v1`), and no semantic set is declared on this
stage, so no `semantic_grades` block is written. `vote_accuracy` is omitted:
votes are never scored off a merits event.

**Outcome match.** Predicted `denied` at P(grant) = 0.03; actual `denied`.
`correct = 1`, `brier_score = (0.03 - 0)^2 = 0.0009`. Both are my elicited
reads; the stamp recomputes them from the committed artifacts.

**What the rationale got right.** The candidate anchored on the correct
strictly-prior pool (31/296 ≈ 10.5%) and then moved off it for three reasons
that are each the right reason: the heightened standard for an injunction
pending appeal (an "indisputably clear" entitlement, citing *Ohio Citizens for
Responsible Energy* and *Respect Maine PAC*), the state-law character of the
signature-sample and affidavit dispute with no freestanding federal right to a
state initiative, and the Purcell-type timing problem of adding a measure to a
ballot days before the state's settlement date. It also kept the number off the
floor for a stated reason (sympathetic margin story, experienced counsel), which
is disciplined rather than reflexive. The forecast document — read for context
only, not scored — named "a single-Justice or unexplained-order denial by
September 3–4" as the modal path, which is what happened. The ladder
increments were each reasoned separately from the statpack's escalation
columns with the censoring caveat stated; the increments themselves are the
harness's to score and I do not fold them into `reasoning_quality`.

**Where it is weaker.** (1) The candidate could not read the application (its
PDF fetch returned 403, and `record/documents/` was not provisioned at
prediction time), and says so — an honest disclosure — but the analysis of the
federal theories therefore rests on press coverage rather than the applicants'
own framing. (2) It describes the Michigan Supreme Court as having "declined
relief" / issued a "refusal", whereas the application itself pleads
*constructive* denial by inaction: the state court had simply not acted. That
distinction bears on the §1257 posture (no state-court judgment at all, not an
adverse one) and the candidate did not engage it. (3) The referral estimate
(0.55) ran against what happened — a single-Justice denial — though the
reasoning behind it (modern practice referring salient substantive
applications) is a fair prior and is not what `reasoning_quality` measures.

**`reasoning_quality` = 0.80.** Sound standard, correct pool, correct direction
and magnitude of adjustment, honest about its evidentiary limits; docked for
mischaracterizing the state-court posture and for not having the application's
own arguments in hand.

**Leakage.** Mode `forward`, `retrieved_outcome_material = false`,
`influenced_prediction = not_applicable`, `leakage_suspected = false`. All 24
captured calls are timestamped 2026-09-01, two days before the denial; coverage
1.0; the only legible document date is 2026-08-31. The web searches surfaced
pre-decision reporting (board deadlock, signature counts, deadlines) and the
candidate disclosed that reliance as forward signal — a point for the cell's
integrity. Nothing in the log or prose is a disposition of this application,
and the case was genuinely open when the cell ran, so no mis-provisioning flag.

**Big case.** My independent read is 0.4 (see `evaluation.json`). One caveat on
independence: the staged `prediction.json` carries the predictor's
`big_case_score` in the same document as the fields I had to read first, so I
saw it before forming my own; my read is drawn from the record — the
application text, the docket, and the single-Justice disposition — not from
that number.

**Retrieval.** None beyond the provisioned inputs and the committed statpack;
see `../../20260904T183332Z/retrieval.md`.
