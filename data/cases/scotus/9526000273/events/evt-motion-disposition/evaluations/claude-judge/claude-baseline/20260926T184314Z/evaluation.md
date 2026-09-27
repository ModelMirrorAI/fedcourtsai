# Evaluation: claude-baseline — scotus/9526000273, evt-motion-disposition

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
(about 10.5%) that clears the floor; a null stamp would be about the pack,
not the pool. `claim_scores` (the `interim-v1` set) is the harness's and
untouched.

## Scores

- `correct = 0`. The prediction named `denied`; the outcome label is
  `withdrawn`. No candidate could have named a withdrawal, so this bit is
  uninformative about relative skill on this cell (see the flag).
- `brier_score = 0.0009`: probability 0.03 against `actual_granted = 0`, the
  best of the three on the binary that resolved.
- `vote_accuracy` omitted (not a merits cell). No `semantic_grades` block
  (no semantic set on an interim event).

## Reasoning quality: 0.85

Judged on `reasoning.md` alone. This is the most disciplined of the three
rationales:

- The baseline is computed in the open (17/226 + 14/70 = 31/296) and read
  on the section's own terms, including that it is the scored rate and that
  no band applies. The population mismatch argument is then made
  empirically rather than asserted: the candidate pulled recent corpus rows
  and reports that all twelve capital rows, and all five recent capital stay
  applications it names, were denied, while the pool's recent grants were
  government emergency applications. That is the right way to justify a
  sharp move off the pooled rate.
- The doctrinal read is correct and correctly bounded: *Woodard* leaves a
  clemency-procedure challenge little due-process foothold, so the
  fair-prospect-of-certiorari prong is the weak link.
- It states where it is weakest. No filing text was provisioned at
  prediction time (the record's `documents.json` shows the application was
  fetched on 2026-09-05, after the cell ran), and the candidate says its read
  of claim strength is inferred from parties, lower court, and posture, and
  names that as "the main place to discount me." That is accurate: it did
  not see the quorum-statute argument, the preservation objection, or the
  Court's refusal of the waiver on the linked petition, all of which
  codex-baseline extracted from the filings.
- It is the only rationale that names withdrawal and mootness as routes by
  which an application resolves without Court action, which is exactly what
  happened, even though it raises them only to cap the referral figure
  rather than as a disposition scenario.
- Its corpus-vintage note is honest about what `corpus-info` could not do
  in the cell and substitutes the retrieval evidence instead.

The main deductions: the decision not to read the filings was defensible on
leakage grounds but cost real information, since the official PDFs were
linked in the provisioned snapshot and dated before the cell ran; and, like
the others, the disposition forecast treats grant and denial as the whole
space.

## Leakage

Forward cell, `influenced_prediction = not_applicable`,
`retrieved_outcome_material = false`, `leakage_suspected = false`. The
prediction was created 2026-09-01; the application stayed pending until
2026-09-25, so no disposition existed to retrieve.

The harness log holds 24 rows with `result_capture_coverage = 1.0`, all
`shell`, `file-read`, or `file-write`. Three corpus queries ran through the
cell service (the candidate's `retrieval.md` records the `ranged corpus
reads` lines); the newest `retrieved_doc_date` is 2026-08-28. No MCP call
and no web search appears, matching the candidate's statement that it
deliberately avoided live retrieval about this docket. Nothing dated at or
after the resolution appears anywhere.

## Big case

My own read is 0.25 (see `big_case.notes`). Disclosure: the predictor's
`big_case_score` sits in the staged `prediction.json`, which I read before
writing this, so the read is independent in its reasons but was not formed
without exposure to their number.
