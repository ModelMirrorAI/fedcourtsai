# Evaluation: gemini-baseline — scotus/9526000273, evt-motion-disposition

## Stage and outcome

This is an **interim** cell: application 26A273, a stay of execution pending
certiorari (linked petition 26-5211), submitted to Justice Thomas on
2026-08-28. The outcome is `actual_disposition = withdrawn`,
`actual_granted = 0`, resolved 2026-09-25: the applicant withdrew the
application by letter after the scheduled 2026-09-16 execution date had
passed. No order on the application was entered, no response was requested,
no referral was docketed, and no amicus brief was filed.

Because the cell is interim, `segment_base_rate` and `brier_skill_score` are
the harness's: `stamp-cell` pools the statpack's substantive-application
slice over application-Terms strictly before OT2026 and writes both, or
clears them where the pool is under the 50-resolved floor. I wrote neither
and left `base_rate_basis` null. For orientation, the committed statpack
shows OT2025 17/226 and OT2024 14/70, a strictly-prior pool of 31/296
(about 10.5%) that clears the floor; a null stamp would therefore be about
the pack, not the pool. `claim_scores` (the `interim-v1` set) is the
harness's and untouched.

## Scores

- `correct = 0`. The prediction named `denied`; the outcome label is
  `withdrawn`. No candidate could have named a withdrawal, so this bit is
  uninformative about relative skill on this cell (see the flag).
- `brier_score = 0.0025`: probability 0.05 against `actual_granted = 0`.
- `vote_accuracy` omitted (not a merits cell). No `semantic_grades` block
  (no semantic set on an interim event).

## Reasoning quality: 0.40

Judged on `reasoning.md` alone. The rationale is a single paragraph and a
disclosure line. What it gets right:

- It cites the correct pooled baseline (about 10.5% over OT2024 and OT2025)
  and adjusts downward for the capital-stay class.
- Its ladder calls are sensible and correctly reasoned from the record: a
  response is already on file so a formal request is unlikely; capital
  applications are routinely referred; late amicus filings are rare.
- It discloses its one external lookup (the execution date) and states that
  it revealed no outcome.

What is missing is any engagement with the case. The rationale never says
what the application is about: the Georgia clemency-board recusal and quorum
dispute, *Woodard*, the state-law posture, the preservation problem, or the
fact that the Court had declined the respondents' waiver on the linked
petition. "Capital stays face a significantly higher bar and are granted
less frequently" is asserted without a source or a number, when the corpus
and the provisioned snapshot both offered material to ground it. The
downward adjustment from 10.5% to 5% is therefore a category prior, not an
analysis of this application, and the rationale would read identically for
any capital stay application. Like the others, it does not consider
withdrawal or mootness as a route. The number was well placed for the
binary that resolved, but the document gives a reader little basis to trust
that placement beyond the class prior.

## Leakage

Forward cell, `influenced_prediction = not_applicable`,
`retrieved_outcome_material = false`, `leakage_suspected = false`. The
prediction was created 2026-09-01; the application stayed pending until
2026-09-25, so no disposition existed to retrieve.

The harness log holds 26 rows with `result_capture_coverage = 0.0`: every
marker-carrying row is `unobserved`, which is this engine's standing
telemetry shape and not a defect, so each call is graded on its query. The
one `web-search` row queries the applicant's execution date, a scheduling
fact the candidate disclosed in both prose documents together with a
statement that the stay remained pending. The rest are provisioned-file
reads, statpack reads, two corpus queries (the first failed on its date
filter, per the candidate's own `retrieval.md`), and the output writes.
Nothing dated at or after the resolution appears anywhere.

## Big case

The prediction carries no `big_case_score`, which is a valid record and not
a mark against it. My own read is 0.25 (see `big_case.notes`); the other
candidates' scores were visible in their staged files before I wrote it,
so the read is independent in reasoning but not in exposure.
