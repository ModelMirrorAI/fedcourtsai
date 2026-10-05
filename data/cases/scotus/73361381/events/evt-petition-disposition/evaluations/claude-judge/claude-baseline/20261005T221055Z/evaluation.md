# Evaluation: claude-baseline — scotus/73361381, evt-petition-disposition

## Outcome and scores

Cert-stage, forward cell. The petition (No. 25-1291, Chaganti v. Cincinnati
Insurance Co., pro se, paid) was distributed once for the September 28, 2026
conference and **denied** on the October 5, 2026 order list, with no noted
dissent and no call for a response.

- `correct` = 1: `predicted_disposition` `denied` matches `actual_disposition`
  `denied`.
- `brier_score` = (0.004 − 0)² = 0.000016.
- `segment_base_rate` = 0.0512, basis `risk_set`. The prediction froze
  `band: baseline` under `salience_version: sal-v4`, matching the statpack
  table's heading, so I pooled the bracketed `reached` figure for `baseline`
  resolved-weighted over OT2017–OT2024 (the eight rendered Terms strictly
  before the case's Term 2025): ≈593 weighted grants over n = 11,580. The
  table renders 10 of 10 Terms and the in-code ten-Term lookback reaches the
  same eight rows, so there is no window divergence to flag. The candidate
  computed the identical pool (its own table of eight rows, "roughly 5.1%").
- `brier_skill_score` = 1 − 0.000016 / 0.0512² ≈ 0.9939.
- `vote_accuracy` omitted (cert stage; no votes are ever scored here).

## Reasoning quality: 0.85

This is the strongest of the three rationales. It anchors on exactly the
right baseline, shows its pooling, and then discounts for reasons that are
specific to this petition and sourced:

- **Preservation.** It retrieved the Ohio Tenth District opinion
  (2025-Ohio-1982, decided June 3, 2025, well before the snapshot) and reports
  that it resolves the case on the text of S.B. 224 Section 4, the Ohio
  Retroactivity Clause, and waiver, with no federal due-process analysis. From
  that it draws the correct inference that the sole federal question looks
  unpreserved under 28 U.S.C. § 1257, which is the single best reason to expect
  denial and one the other candidates did not reach. It also says exactly
  where that reading is vulnerable (the Ohio Supreme Court memorandum it did
  not retrieve), which is the right kind of hedge.
- **Merits of the theory.** It identifies the petition's own concessions
  (clear retroactive intent; eight years is a reasonable time) and the Texaco
  v. Short "enact and publish" line that the remaining argument runs against.
  Both are accurately drawn from the petition text at pages 6–8.
- **The asserted split.** It explains why Tabbaa and the S.D. Ohio footnote
  are not a split (dicta, same district later applied S.B. 224) and why an
  intra-state disagreement over a state statute would not be certworthy
  anyway.
- **Posture and petitioner history.** No response, no waiver, no amici, 16
  pages, a prior denied petition by the same petitioner. All consistent with
  the snapshot and the retrieved record.

The claim-by-claim section is coherent: the relist increment (0.08) is
reasoned from the no-response long-conference posture rather than copied
from the terminal relist cut, and it says which route (a call for a response)
would most plausibly add a distribution.

Minor deductions: the number is defended over a 0.2%–1% range without
saying why 0.4% rather than the pooled-anchor-times-discount it implies; the
"serial pro se petitioners grant at rates well below the paid population"
claim is asserted without a figure; and the petition's internal inconsistency
(a "2014" complaint against a March 2024 filing date) goes unremarked, though
it changes nothing.

## Leakage

`mode` forward; `retrieved_outcome_material` false; `influenced_prediction`
`not_applicable`; `leakage_suspected` false. The log carries 23 calls with
`result_capture_coverage` 1.0. The external calls are nine CourtListener
lookups: opinion searches that found the Ohio Tenth District decision
(`retrieved_doc_date` 2025-06-03), a full read of that opinion, a party-name
opinion search, a SCOTUS docket lookup for 25-1291 (`retrieved_doc_date`
2026-05-19, the filing date; the prose records `date_terminated` null), and a
docket-entries call that returned nothing. Two `fedcourts query` calls
returned unrelated 2020s grants and denials. Every dated document precedes
the 2026-09-16 snapshot; nothing postdates the 2026-10-05 resolution, and the
reasoning nowhere presupposes the outcome. The candidate's retrieval note
says it encountered no disposition, which the log bears out. The case was
genuinely open when predicted.

## Big-case read

My own read, formed from the petition and record: 0.04. One pro se
assignee's time-barred 2010 insurance claim; a notice-by-codification theory
that cites no conflict beyond intra-Ohio dicta, drew no response, no amici,
and no writing on denial.

## Not scored

The claims block and `predicted_reasoning.md` are not graded here; the
harness scores the declared claims in code. No semantic set is declared on a
cert cell, so no `semantic_grades` block is written.
