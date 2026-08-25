# Evaluation — claude-baseline, evt-brief-response-disposition (scotus/9526000124)

## The cell and the scored numbers

This is an **interim** cell (`stage: interim` in `event.yaml`): the disposition
of the government's stay application in Trump v. California, forecast at the
response-filed moment. The realized outcome is **granted**
(`actual_disposition: "granted"`, `actual_granted: 1`, resolved 2026-08-24).

claude-baseline predicted **denied** at probability **0.15**, so `correct = 0` and
`brier_score = (0.15 - 1)^2 = 0.7225`.

The baseline and skill are the harness's on an interim cell: `stamp-cell`
pools the statpack interim section's substantive grant rate over application
Terms strictly before this one and writes `segment_base_rate` and
`brier_skill_score` itself, so I write neither, and `base_rate_basis` stays
null structurally (an application freezes no band). The committed statpack
supports that pool: Terms 2025 (16/178) and 2024 (14/47) give 30/225 ≈ 13.3%,
clearing the pre-registered 50-resolved floor, so the stamped rate should come
back non-null. `claim_scores` is likewise the harness's (`interim-v1`).
The prediction's frozen `context.band` is null — the ordinary interim shape,
no flag needed.

## What the prediction got right and wrong

Wrong on the only scored axis: it called denial at 0.15 and the Court granted
the stay. Its Brier is the worst of the three candidates.

Much of the surrounding forecast was nonetheless accurate: referral to the
full Court at 0.93 (the outcome records `referred_to_court: true`), no second
response request (correct), disposition within one to three weeks of
prediction (the order came eight days later), and the expectation of separate
writings on a contested emergency election matter. It also correctly treated
the response-request rung as already fired and vacuous, and its careful note
on the amicus counter's singular/plural semantics was sound diligence.

## What drove `reasoning_quality` (0.55)

This is the most thorough rationale of the three: correct strictly-prior
baseline (30/225 ≈ 13.3%) with honest caveats about parse coverage and
escalation selection, explicit up/down adjustments, an explicit account of the
denial-first collapse of partial relief, and a candid statement of its largest
uncertainty — "if the Court treats this like an ordinary intra-branch
injunction fight rather than an election case, 0.15 is too low." That named
risk is what happened.

The score sits at 0.55 rather than higher because the analysis affirmatively
weighted three signals toward denial that the outcome undercuts, and weighted
them heavily: (1) revealed preference from the un-entered administrative stay
and twenty-day pendency (long pendency, as it itself conceded, accompanies
grants with writings too); (2) a strong Purcell reading, treating the
injunction as the settled status quo; and (3) a confident merits call that
there was "no plausible source of presidential authority," leaving the number
barely above the pooled baseline despite recognizing that the
government-applicant conditional "taken alone would put the number well above
the baseline." The process was disciplined and self-aware; the weighting
judgment on the case-specific signals was wrong, and commentary
(Hasen/Election Law Blog) was leaned on where filings' text was unavailable.
It did not engage the applicants' justiciability/ripeness route, which its
better-scoring rival identified as the likely grant path.

## Leakage

`forward`, and genuinely so: the case was open at the 2026-08-16 snapshot and
resolved 2026-08-24. The log's queries confirm pendency rather than seeking a
disposition; the one legible retrieved-document date (2026-08-14) predates
resolution. `influenced_prediction = not_applicable`, `leakage_suspected =
false`. No sign of a mis-provisioned decided case.
