# Evaluation — codex-baseline — Fairfield Sentry Ltd. v. Citibank NA London (scotus/73281372, evt-petition-disposition)

## Outcome and scores

The petition was **denied** on the October 5, 2026 order list after its first
distribution (Conference of September 28, 2026): no relist, no CVSG, no noted
dissent; Justice Alito took no part. `actual_granted` = 0.

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.16 − 0)² = **0.0256**.
- `segment_base_rate` = **0.0512**, basis `risk_set`. The prediction froze
  `band: baseline` under `salience_version: sal-v4`, matching the statpack
  table heading. Pooled bracketed `reached` figure for `baseline`,
  resolved-weighted over OT2017–OT2024 (the eight rendered Terms strictly
  before Term 2025): 592.9 / 11,580 ≈ 5.12%, the same figure the candidate
  itself computed from the pack. The caption renders 10 of 10 Terms, so no
  window divergence.
- `brier_skill_score` = 1 − 0.0256 / 0.0512² = **−8.77**. The highest
  probability of the three on a denied petition, and the worst skill.

Cert cell: no `vote_accuracy`, `judgment_correct`, `semantic_grades`, or
`claim_scores` is mine to write.

## Reasoning quality: 0.72

What drove the score up:

- The anchor is the best-documented of the three: pooled from
  `statpack.json`'s per-Term reached rows to 593 / 11,580 = 5.12%, with the
  exclusion of the case's own Term stated and the terminal-rate fallback
  explicitly rejected for the right reason.
- It is disciplined about what the statpack's cuts can and cannot do:
  it declines to multiply the relist and CVSG cuts as independent signals
  and declines to lower the anchor to the relist-0 terminal rate, both of
  which are correct readings of the pack's caveats.
- The legal analysis engages the actual conflict claims: Condor concerned
  §1521(a)(7) rather than §§546(e)/561(d); Frost and Grede barred the
  claims by a different mechanism; the direct-bar versus implied-preemption
  distinction matters most where the underlying law is foreign. It weighs
  the BIO's vehicle objections (300 adversary proceedings, alternative
  grounds) and the petition's answer.
- It states its information set precisely (what was truncated, what was
  not provisioned, that no precedent text was independently verified) and
  does not fill gaps with invented facts.

What held it down:

- The number is detached from the analysis. The candidate concludes the
  asserted split is "not a verified square conflict", that the vehicle
  objections are "genuine reasons to prefer further development", and that
  counsel and amici are "modest" signals, then triples the anchor to 16% on
  "judgment". A rationale whose every substantive finding points down
  should not land at the highest number on the cell.
- It does not use the Court's handling of prior Madoff safe-harbor
  petitions or the first-distribution long-conference posture as evidence,
  both of which were available and both of which pointed at a routine
  denial. It mentions the BIO's reference to a 2015 denial and sets it aside.
- The prose is long and heavily hedged; several paragraphs disclaim rather
  than analyze, which is honest but dilutes the argument-to-length ratio.

## Leakage

Forward cell. The prediction was created 2026-09-16, before the conference
and the denial. The log carries 27 calls, 25 captured. The two `unobserved`
rows are a web search for the text of 11 U.S.C. §561(d) and Supreme Court
Rule 10 and a page open of the statute at Cornell LII, graded on their
queries: general legal research, not this case. The one CourtListener call
sought the Condor opinion by citation (601 F.3d 319) and returned HTTP 429.
No query names this docket, its disposition, or `data/qp-topics/`.
`retrieved_outcome_material` = false, `influenced_prediction` =
`not_applicable`, `leakage_suspected` = false. The candidate's own account
matches the log.

## Big case

My independent read is 0.40, formed from the record before weighing the
candidate's own score: roughly $6 billion in Madoff feeder-fund clawback
claims and a first-impression Chapter 15 / §546(e) question of real interest
to the cross-border insolvency bar, but a technical commercial dispute with
little public salience, denied at first conference without CVSG, relist, or
separate writing.
