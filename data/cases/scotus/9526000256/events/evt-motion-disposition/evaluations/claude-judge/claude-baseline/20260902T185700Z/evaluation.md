# Evaluation — claude-baseline, evt-motion-disposition (interim)

**The cell.** Interim stage (`event.yaml: stage: interim`): a pro se
application (26A256) for injunctive relief against the U.S. District Court for
the N.D. of Georgia, submitted to Justice Thomas. Realized outcome: **denied**
by Justice Thomas on 2026-08-28 (`actual_granted` = 0), with every escalation
signal at zero (no response requested, no referral, no amicus).

**Scores.** The prediction named `denied` — `correct` = 1. Brier on the
elicited P(grant) = 0.01 is **0.0001**. Because this is an interim cell, the
baseline and skill are the harness's: `segment_base_rate` and
`brier_skill_score` are stamped by `stamp-cell` from the committed statpack's
interim section, `base_rate_basis` stays null structurally (the interim pool is
no band product), and the `claim_scores` block over the declared `interim-v1`
set is likewise computed in code. For the reader of the stamped rate: the
current committed statpack's strictly-prior pool for a Term-2026 application is
Terms 2025 + 2024 = 296 resolved substantive applications, 31 granted (~10.5%),
clearing the 50-resolved floor — so a null stamp would indicate a pack problem,
not a thin pool. No `vote_accuracy`: votes are never scored off the merits
stage.

**Reasoning quality: 0.90.** The strongest of the three candidates. It read
the cell correctly (interim, arrival moment, ladder at zero), anchored on the
statpack's pooled strictly-prior rate and quoted it with the right caveats
(right-censored escalation columns, uneven Term-2024 parse coverage), then
justified a large downward departure on case-specific grounds: pro se
applicant, respondent is the district court itself, mandamus as the proper
vehicle, and the All Writs standard far beyond the visible record. It did
real retrieval work — locating the applicant's two underlying N.D. Ga. ADA
suits and confirming the Eleventh Circuit record was unavailable — and
disclosed its main gap (the application PDF was not retrieved) honestly. Its
quoted pool (227 resolved / 30 granted, 13.2%) differs from the current pack
(296/31, 10.5%) because the statpack was refreshed after this cell ran; the
numbers are consistent with the pack vintage at its run time and are not held
against it. The realized outcome matched the analysis in every particular:
one-line denial by the Circuit Justice, no response, no referral, no amicus.

**Leakage.** Mode forward, but the case was in fact already decided: the event
resolved 2026-08-28 and this cell ran 2026-08-29 — a decided case
mis-provisioned into a forward cell (flagged in this run's `flags.json`). The
fully captured log shows no outcome material retrieved (all document dates are
2024 lower-court entries; no disposition-seeking query) and the prose treats
the case as pending, so `retrieved_outcome_material` = false and
`influenced_prediction` = none. The superseded 2026-08-29 snapshot could not
be re-inspected, which the leakage notes record.

**Big case.** My independent read is 0.02: an individual procedural dispute
with no constituency beyond the applicant.
