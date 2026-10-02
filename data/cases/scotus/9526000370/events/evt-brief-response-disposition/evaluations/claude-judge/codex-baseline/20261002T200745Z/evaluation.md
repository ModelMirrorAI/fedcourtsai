# Evaluation: codex-baseline — scotus/9526000370, evt-brief-response-disposition

## Cell and outcome

Interim-stage cell (stay application 26A370, Thornell v. Jensen), moment
`response-filed`, opened 2026-09-25. Outcome: **denied**, `actual_granted` 0,
resolved 2026-10-01 by Justice Kagan alone ("Application (26A370) denied by
Justice Kagan"): no referral, no amici, no writing. `interim_signals`:
response requested true, referred false, amici 0.

The cell is interim, so the baseline and skill are the harness's:
`stamp-cell` pools the statpack's substantive-application grant rate over
application-Terms strictly before 2026 and writes `segment_base_rate` and
`brier_skill_score`, clearing both below the 50-resolved floor. I wrote
neither and left `base_rate_basis` null. The committed interim table's
strictly-prior rows with resolved substantive counts (Term 2025: 17 of 226;
Term 2024: 14 of 70) pool to 31 of 296, about 0.105, above the floor, so a
non-null stamp is expected; a null would point at the pool. `claim_scores`
(`interim-v1`) is the harness's and not assessed here. No `vote_accuracy`
(not merits) and no `semantic_grades` (no semantic set on an interim event).

## Quantitative

| field | value | note |
| --- | --- | --- |
| predicted_disposition | granted | outcome denied → `correct` 0 |
| probability | 0.58 | Brier (0.58 − 0)² = 0.3364 |

Written per their definitions as the independent read; the committed values
are the stamp's.

## Reasoning quality: 0.55

Strengths. The rationale is disciplined about its information boundary: it
names the snapshot vintage, the date cutoff, the truncated application text,
and the fact that it could not read the respondents' opposition, and it
refuses to attribute arguments to a brief it did not see. It anchors on the
right statpack pool (31 of 296) with the right coverage caveats (972 unparsed
2024 applications, selection on the escalation ladder). It engages the
contrary evidence concretely rather than as boilerplate: the district court's
August 5 order disputing that intermediate measures were skipped, the
contempt history and fines, the reset-the-clock framing on which the
"first resort" argument depends, Judge Forrest's limited partial dissent. It
gives the CASA theory little weight, which the outcome bears out. And it kept
denial "quite plausible", pricing the realized outcome at roughly 0.42.

Weaknesses. The upward adjustments that carry it from 0.105 to 0.58 are mostly
about stakes and practical asymmetry (a large institutional handover before an
expedited appeal is heard), not about the applicants' likelihood of success
or the Court's emergency-docket practice. It does not weigh certworthiness,
the criterion several Justices have said the emergency docket tracks, and the
application's cert argument is thin. It does not price the interlocutory
posture against Circuit Justice practice: with an expedited appeal pending and
a motions panel that expressly left the stay open to the merits panel, denial
by the Circuit Justice without referral was a live shape that the rationale
never names. The handover-asymmetry argument is also weaker than stated once
the district court had already delayed the effective date to October 19. The
candidate itself calls the adjustment "large and judgmental, not an estimated
likelihood ratio", which is honest, but the honesty does not supply the
missing analysis. A careful, well-structured rationale that leaned the wrong
way for reasons that were more about magnitude than merit.

Per the contract, `predicted_reasoning.md` and the claims block are not
scored; the forecast was read for context only.

## Leakage

Forward cell, `leakage.influenced_prediction` = `not_applicable`,
`retrieved_outcome_material` false, `leakage_suspected` false. Coverage 0.92.
The two unobserved rows are a web search for the Nken stay standard and a web
open of the 2026-09-25 opposition PDF named in the snapshot's own docket
entry, a pre-cutoff filing rather than an outcome query; both are graded on
their queries and neither seeks a disposition. All captured calls are local
reads of the contract files, the provisioned snapshot, the application text
and the statpack. The snapshot (2026-09-25) and cutoff (2026-09-26) precede
the 2026-10-01 resolution, so the case was genuinely open when predicted.

## Big case

My own read is 0.5 (see `big_case.notes`).
