# Evaluation: gemini-baseline — scotus/73361381, evt-petition-disposition

## Outcome and scores

Cert-stage, forward cell. The petition (No. 25-1291, Chaganti v. Cincinnati
Insurance Co., pro se, paid) was distributed once for the September 28, 2026
conference and **denied** on the October 5, 2026 order list, with no noted
dissent and no call for a response.

- `correct` = 1: `predicted_disposition` `denied` matches `actual_disposition`
  `denied`.
- `brier_score` = (0.005 − 0)² = 0.000025.
- `segment_base_rate` = 0.0512, basis `risk_set`. The prediction froze
  `band: baseline` under `salience_version: sal-v4`, and the statpack's
  "Segment base rate by salience band (sal-v4)" heading matches that version,
  so I pooled the bracketed `reached` figure for `baseline` resolved-weighted
  over the Terms strictly before the case's Term (2025) that the table renders:
  OT2017 through OT2024, eight rows, ≈593 weighted grants over n = 11,580.
  The table renders 10 of 10 Terms, and the in-code ten-Term lookback
  (2015–2024) reaches the same eight rows since the pack holds nothing before
  OT2017, so there is no window divergence to flag.
- `brier_skill_score` = 1 − 0.000025 / 0.0512² ≈ 0.9905.
- `vote_accuracy` omitted (cert stage; no votes are ever scored here).

## Reasoning quality: 0.55

The rationale is short but points the right way. It anchors on the correct
figure (the bracketed `reached` baseline rate, "~5%" across prior Terms),
then discounts for a pro se petitioner, a fact-bound and state-law-dependent
issue, and the absence of any response before distribution. It correctly
notes that no-response petitions not called for a response are nearly always
denied at first conference, and it prices the increments consistently with
that (relist 0.02, CVSG 0.001).

What holds the score down:

- **No engagement with the petition itself.** The document says nothing about
  what the petition actually argues (notice by codification versus session
  law), the petitioner's concessions that S.B. 224 shows clear retroactive
  intent and that eight years is a reasonable time, or the Texaco v. Short
  "enact and publish" standard that cuts against the theory. The description
  "narrow due process challenge regarding a state court's application of a
  statute of limitations" is accurate but generic; nothing in it is specific
  to this petition's weakness.
- **A loose docket inference.** It says the respondent "has apparently waived
  a response." The snapshot shows no waiver entry; the petition was simply
  distributed after the response date lapsed with nothing filed. The
  conclusion (no response, outright denial) is right, but the stated fact is
  not what the docket shows.
- **No preservation analysis.** The lower court decided the case on Ohio
  statutory text and the Ohio Retroactivity Clause; whether the federal
  question was passed on below is the single strongest reason for denial and
  it goes unmentioned.

The number (0.5%) is well placed and the direction of every adjustment is
sound, so this is competent reasoning, but it reaches the right answer on
heuristics about the posture rather than analysis of the case.

## Leakage

`mode` forward; `retrieved_outcome_material` false; `influenced_prediction`
`not_applicable`; `leakage_suspected` false. The log carries 23 calls, every
one a local read of the provisioned record, the predict prompt, or the
statpack, plus output writes; no CourtListener, web, or corpus call. The
log's `result_capture_coverage` is 0.0, so every call was graded on its
query, and no query names this case's disposition. The case was genuinely
open on 2026-09-17 (snapshot 2026-09-16 shows only the petition and one
distribution) and resolved 2026-10-05, so no outcome existed to leak.

## Big-case read

My own read, formed from the petition and record: 0.04. One pro se
assignee's time-barred 2010 insurance claim; a notice-by-codification theory
that cites no conflict beyond intra-Ohio dicta, drew no response, no amici,
and no writing on denial.

## Not scored

The claims block and `predicted_reasoning.md` are not graded here; the
harness scores the declared claims in code. No semantic set is declared on a
cert cell, so no `semantic_grades` block is written.
