# Evaluation — codex-baseline, evt-motion-disposition (interim)

**The cell.** Interim stage: a pro se application (26A256) for injunctive
relief against the U.S. District Court for the N.D. of Georgia. Realized
outcome: **denied** by Justice Thomas on 2026-08-28 (`actual_granted` = 0),
all escalation signals at zero.

**Scores.** The prediction named `denied` — `correct` = 1. Brier on P(grant) =
0.015 is **0.000225**. This being an interim cell, `segment_base_rate` and
`brier_skill_score` are the harness's (stamped from the committed statpack),
`base_rate_basis` is structurally null, and `claim_scores` over the declared
`interim-v1` set is computed in code. For the reader of the stamped rate: this
candidate's own statement of the pool — Terms 2025 + 2024, 31 grants among 296
resolved substantive applications, 10.47%, clearing the 50-resolved floor —
matches the current committed pack exactly.

**Reasoning quality: 0.68.** Statistically the most rigorous of the three: it
read the current pack correctly, named the floor, and articulated the pack's
own selection caveats better than the pack requires (machine-matchable
disposition text, denial-first reading of partial relief, uneven parse
coverage, and the escalation-ladder selection that makes the scored population
narrower than the pooled cohort — hence skill against the anchor alone not
establishing forecast skill). It was honest about failed retrieval (the CA11
record was unfindable, same-name results not treated as linked) and explicit
that its large downward adjustment was judgmental. What costs it heavily is a
material record-reading miss: its provisioned snapshot (2026-08-31.json)
contains only two docket entries, and the second is the Aug 28 denial itself —
yet the reasoning describes the docket as though the Aug 11 submission were
the last entry ("dated twenty days before the snapshot without a response
request or referral appearing") and the forecast places the disposition in
September 2026. Overlooking the dispositive entry in a two-entry docket is a
serious lapse in reading the primary input, whichever way it cuts. The
substantive legal read (extraordinary relief involving the district court
itself, no escalation signals, denial the strong direction) was sound and the
realized outcome matched it.

**Leakage.** Mode forward, but this cell ran three days after the event
resolved, and — unlike the two 08-29 candidates — its provisioned snapshot
carried the outcome on its face. The captured log shows the snapshot was read
in full, so `retrieved_outcome_material` = true. The evidence of actual use
is negative: no mention of the entry, a future-dated disposition forecast, and
a *less* confident probability than the blind candidates. But an outcome
sitting inside the read input cannot be certified unused, so
`influenced_prediction` = possible and `leakage_suspected` = true. The
mis-provisioning itself is flagged in this run's `flags.json`; the grade is
advisory and segments, it does not change the scores above.

**Big case.** My independent read is 0.02: an individual procedural dispute
with no constituency beyond the applicant.
