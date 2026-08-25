# Evaluation — codex-baseline

**Cell.** Interim stage (`stage: interim`, a stay application forecast at the
response-requested moment), forward mode. The outcome is a straight denial
(`actual_disposition: denied`, `actual_granted: 0`, resolved 2026-08-24), with
`interim_signals` recording the response request, full-Court referral, and two
amicus briefs.

**Score.** Predicted `denied` at P(grant) = 0.38 → `correct` = 1,
`brier_score` = (0.38 − 0)² = 0.1444. This is an interim cell, so the baseline
and skill are the harness's, not mine: `stamp-cell` pools the statpack's
interim substantive slice over application-Terms strictly before this Term-2026
application (Term 2025: 16/178; Term 2024: 14/47 → 30/225 ≈ 13.3%, clearing the
50-resolved floor), so a stamped rate should appear rather than a null.
Against that baseline the 0.38 probability will grade as substantially
negative skill — the naive 13.3% was much closer to the denial. I write
neither `segment_base_rate` nor `brier_skill_score`; `base_rate_basis` stays
null structurally. No `vote_accuracy` (interim votes are never scored, and none
were predicted); `claim_scores` is the harness's.

**Reasoning quality: 0.75.** The strongest retrieval of the three candidates:
it read the district court's stay memorandum, the divided First Circuit order
(majority and partial dissent), and the applicants' own CA1 stay motion, and
its account of the record is accurate. It anchored on the correct strictly
prior pooled baseline (30/225 ≈ 13.3%) and gave a statistically literate
reason for not conditioning on the statpack's escalation-signal counts
(terminal, right-censored, wrong denominator). It identified the decisive
weakness — intervenor states seeking a full stay of an injunction that does not
operate against them, with the CA1 finding their harm case weak — and
correctly reasoned that the denial-first convention collapses partial relief
into `denied`, so the scored probability is for an unqualified grant only.
What keeps the score from higher ground is calibration: a near-tripling of the
baseline to 0.38 on the strength of a response request and a partial dissent
was aggressive given the standing weakness the candidate itself articulated;
its own analysis pointed lower than its number. Honest about the truncated
snapshot and about what it could not see.

**Leakage.** Forward and genuinely open — created 2026-08-20, resolved
2026-08-24. The log shows lower-court and pre-cutoff material only (latest
`retrieved_doc_date` 2026-07-31); its SCOTUS opinion searches were explicitly
bounded to `filed_before: 2026-07-29`. `influenced_prediction` =
`not_applicable`, `leakage_suspected` = false.

**Big case.** My independent read is 0.9 — see the JSON notes. Formed from the
case posture and outcome context, not the candidate's score.
