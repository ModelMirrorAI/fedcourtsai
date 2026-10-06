# Evaluation: codex-baseline — scotus/73361381, evt-petition-disposition

## Outcome and scores

Cert-stage, forward cell. The petition (No. 25-1291, Chaganti v. Cincinnati
Insurance Co., pro se, paid) was distributed once for the September 28, 2026
conference and **denied** on the October 5, 2026 order list, with no noted
dissent and no call for a response.

- `correct` = 1: `predicted_disposition` `denied` matches `actual_disposition`
  `denied`.
- `brier_score` = (0.008 − 0)² = 0.000064.
- `segment_base_rate` = 0.0512, basis `risk_set`. The prediction froze
  `band: baseline` under `salience_version: sal-v4`, matching the statpack
  table's heading, so I pooled the bracketed `reached` figure for `baseline`
  resolved-weighted over OT2017–OT2024 (the eight rendered Terms strictly
  before the case's Term 2025): ≈593 weighted grants over n = 11,580. The
  table renders 10 of 10 Terms and the in-code ten-Term lookback reaches the
  same eight rows, so there is no window divergence to flag. The candidate
  computed the identical pool (5.12% over 11,580).
- `brier_skill_score` = 1 − 0.000064 / 0.0512² ≈ 0.9756.
- `vote_accuracy` omitted (cert stage; no votes are ever scored here).

## Reasoning quality: 0.75

A careful, well-sourced rationale that reaches a sound number by analysing
the petition rather than its posture. Its strengths:

- **Correct baseline, correctly chosen.** It uses the bracketed reached rate
  rather than the terminal rate, pools the right eight Terms, and says why
  the private petitioner stays in `baseline` rather than `state`.
- **Engagement with the petition's weakness.** It identifies the concessions
  (clear retroactive intent, reasonable eight-year transition), reads the
  transition provision from its quoted text rather than the petition's looser
  paraphrase, and characterises the asserted conflict accurately: an
  intermediate Ohio decision and a district-court footnote about how S.B. 224
  was applied, not holdings that due process requires codification.
- **Verified doctrine.** It retrieved the Texaco v. Short passage at 454 U.S.
  532–33 and states the inference narrowly: the petitioner must explain why
  enacted and published session law fails the general standard despite
  conceding a reasonable transition. That is the right use of an authority
  check.
- **Honest about its limits.** It did not retrieve the lower-court opinion,
  so it declines to assert waiver, an adequate state ground, or a
  preservation bar, and says so. It also catches the petition's internal
  "2014" versus "March 2024" inconsistency and explains why it does not treat
  it as a jurisdictional fact.

What holds it below the strongest rationale:

- **The preservation question is left unexamined** when the lower-court
  opinion was one CourtListener call away. The rationale's own caution about
  not inventing a vehicle defect is right, but the result is that the most
  decisive reason for denial is absent from the analysis and the number rests
  on doctrine and conflict alone.
- **Boilerplate crowds the analysis.** Two paragraphs on record vintage,
  corpus-wide refresh stamps, and what the statpack does not establish about
  blob freshness bear on nothing in the forecast; the discipline is welcome
  but the space would have been better spent on the record.
- **The stakes rationale overreaches.** The reasoning puts 0.24 on the
  big-case dimension on the strength of what a ruling could reach, while
  conceding the vehicle makes that ruling implausible. That is graded by
  rank-agreement elsewhere, not here, but as a piece of reasoning it weighs
  a hypothetical holding over the case as framed.

## Leakage

`mode` forward; `retrieved_outcome_material` false; `influenced_prediction`
`not_applicable`; `leakage_suspected` false. The log carries 26 calls with
`result_capture_coverage` 0.96. The external calls target Texaco v. Short
only: one web search for the Texaco citation (`unobserved`, so graded on its
query, which names no party or docket of this case), a CourtListener citation
search, a case-name search, and a passage search for "enact and publish" in
opinion 9428577. No call names Chaganti, docket 25-1291, or this case's
disposition; `retrieved_doc_date` is null throughout. The reasoning reads the
2026-09-16 snapshot and the petition and states it consulted no subsequent
history. The case was genuinely open when predicted and resolved 2026-10-05.

## Big-case read

My own read, formed from the petition and record: 0.04. One pro se
assignee's time-barred 2010 insurance claim; a notice-by-codification theory
that cites no conflict beyond intra-Ohio dicta, drew no response, no amici,
and no writing on denial.

## Not scored

The claims block and `predicted_reasoning.md` are not graded here; the
harness scores the declared claims in code. No semantic set is declared on a
cert cell, so no `semantic_grades` block is written.
