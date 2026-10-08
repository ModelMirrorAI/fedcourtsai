# Evaluation of codex-baseline — scotus/73500287, evt-petition-disposition

## Cell and outcome

Cert-stage cell (`event.yaml` stage `cert`, moment `distribution`). The
petition in *Endure Industries, Inc. v. Vizient Inc.*, No. 25-1385, was
distributed once (June 24, 2026, for the September 28 conference) after the
respondent waived its response; a single amicus brief followed on July 16. The
Court denied the petition on October 5, 2026, with no call for a response, no
relist, and no noted dissent. `outcome.json`: `actual_disposition: denied`,
`actual_granted: 0`, `distribution_count: 1`.

## Scores

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.035 − 0)² = 0.001225.
- `segment_base_rate` = 0.0512, basis `risk_set`. The prediction's frozen
  context carries `band: baseline` and `salience_version: sal-v4`, matching
  the statpack table heading, so the bracketed `reached` baseline figures were
  pooled resolved-weighted over the rendered Terms strictly before Term 2025
  (2017–2024, weighted n = 11,580). The table renders 10 of 10 Terms, so no
  lookback divergence arises. The candidate's own anchor (5.12%, computed from
  `metrics/statpack.json`) is the same pool.
- `brier_skill_score` = 1 − 0.001225 / 0.0512² ≈ 0.533.
- `vote_accuracy` omitted: cert stage, never scored.
- `reasoning_quality` = 0.72.

## What the reasoning got right and wrong

The information-set discipline is the best on the cell: the candidate
separates the sealing-motion distribution and grant (May 26, June 15) from the
petition's single June 24 distribution, notes that the amicus entry's
"Distributed" parenthetical is not a second conference, and states exactly
what it did and did not read. The base rate is pooled exactly from the
matching sal-v4 table, and the terminal relist and CVSG cuts are correctly
treated as shape rather than as prospective hazards. The *Whole Foods* check
through CourtListener (the Ginsburg concurrence on rehearing describing the
fractured decision's limited precedential reach) is a real contribution to the
split analysis, and the candidate is honest that it did not verify *Newcal*
or the Fifth Circuit opinion independently.

The weakness is in the weighting. The candidate names the decisive negatives
(waiver, no call for a response twelve weeks after distribution with the
conference ten days away, one solo amicus, an imperfect split) but discounts
the 5.1% anchor only to 3.5%, declining to treat the waiver as near-dispositive
because the amicus arrived after the first distribution. That under-engages
with the mechanism: a paid petition on a waiver is granted only after a
response is requested, and by the snapshot date that hazard was small, which
the other analyses on this cell priced explicitly and this one did not. The
"reasons to take the petition seriously" section also leans on the petition's
own account of the stakes. Some of the document (package-cache notes, repeated
disclaimers) is process narration rather than analysis. The conclusion was
right and the surrounding reasoning sound, but the number is less well
justified by the analysis than the other candidates' numbers are by theirs.

## Leakage

Forward mode, log coverage 0.93 (30 calls, two unobserved). The two unobserved
calls are a web search for Supreme Court Rule 10 text and a fetch of the
Court's rules PDF; graded on their queries, they name no party, docket, or
disposition. Captured external calls: a CourtListener citation search for
548 F.3d 1028 and a read of opinion 9852752, both 2008 *Whole Foods*
materials. One shell call ran `find data -name AGENTS.md -not -path
'data/qp-topics/*'`. The forbidden path appears only as an exclusion
predicate: the command lists files named `AGENTS.md` and nothing else, so no
qp-topics membership reached the candidate. It is recorded in `flags.json` as
an edge against the literal "query names `data/qp-topics/`" wording and not
graded as outcome-material retrieval. No document dated at or after October 5,
2026; the reasoning states it did not retrieve this case's current docket or
outcome. `influenced_prediction` `not_applicable`,
`retrieved_outcome_material` false, `leakage_suspected` false.

## Big case

Independent read 0.2: a private antitrust market-definition dispute from the
Fifth Circuit, decided at summary judgment, with a waiver, one solo
practitioner amicus, and a silent denial. The Brown Shoe submarket question
recurs, but this vehicle carried no institutional stakes.
