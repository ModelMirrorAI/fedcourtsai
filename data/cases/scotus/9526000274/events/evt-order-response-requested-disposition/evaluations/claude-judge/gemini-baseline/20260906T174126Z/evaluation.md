# Evaluation — gemini-baseline

**Cell:** `scotus/9526000274`, `evt-order-response-requested-disposition`,
stage **interim** (emergency stay application 26A274, NRCC et al. v. Brown et
al.). Outcome: `granted` on 2026-09-04 — the Chief Justice referred the
application to the Court the same day and the Court stayed the Fourth
Circuit's mandate pending certiorari, per curiam, Justice Jackson dissenting.

## Headline

- `predicted_disposition` = `denied` vs actual `granted` → **`correct` = 0**.
- `probability` = 0.15, `actual_granted` = 1 → **`brier_score` = 0.7225**.
- `segment_base_rate`, `brier_skill_score`, `base_rate_basis`: **not
  written.** This is an interim cell, so the baseline (the substantive slice's
  grant rate pooled over application-Terms strictly before OT2026) and the
  skill derived from it are the harness's — `stamp-cell` pools them from the
  committed statpack and clears them below the registered floor. For the
  reader's orientation only: the pack's strictly-prior rows are Term 2025
  (17/226) and Term 2024 (14/70), 31/296 ≈ 10.5%, well above the floor of 50,
  so I expect the stamp to land a rate rather than a null; if it comes back
  null, the section itself is what to read.
- `vote_accuracy` omitted (interim stage — never scored). `judgment_correct`
  null (no judgment on either side). No `semantic_grades` (no semantic set is
  declared off the merits stage). `claim_scores` left to the harness.

## What the prediction got right and wrong

The candidate anchored correctly: it pooled the two strictly-prior Terms to
31/296 ≈ 10.5%, which matches the committed statpack, and it recognised that
the Chief Justice's response request is an affirmative signal. It then moved
only to 0.15 — barely off the unconditioned base rate for an application that
sat at the strongest escalation rung the pack records — and predicted denial.

What drove the miss is what the analysis did not engage with. The provisioned
snapshot already showed a response from the United States and the FCC filed
the same day the response was requested, three days ahead of the deadline;
the candidate's own CourtListener lookups (two caption searches and a docket
endpoint call, all with unobserved results) were never turned into any
account of *why* that filing mattered — the federal respondents supported the
stay, the panel below was divided, the Fourth Circuit had denied its own stay
2–1 and made its judgment effective immediately days before the general-
election advertising window opened, and the applicants carried a circuit
split on Hobbs Act finality. None of that appears. The reasoning's substantive
content is one generic sentence ("the applicant faces the high burden of
showing irreparable harm and a fair prospect of reversal, which is rarely
met") plus a nod to "election-related or major agency rule challenges" —
reasoning that would have produced the same number on almost any
response-requested application.

There is also a framing slip: the application is described as "an emergency
stay … against an FCC ruling (Brown v. FCC)". The applicants were seeking to
*preserve* the FCC Media Bureau's notice by staying the Fourth Circuit's
vacatur of it; the FCC was on their side. That mis-orientation is consistent
with the candidate never having identified who wanted what.

The sub-forecasts I do not score (referral at 0.6, no additional amicus at
0.8) are noted only as context: the docket went on to record a referral and
an accepted amicus brief before disposition.

## `reasoning_quality` = 0.30

Credit for a correctly computed, correctly bounded baseline and for
recognising the direction of the response-request signal. Heavy discount for
an analysis that never reached the case-specific facts available on the
snapshot and through its own retrieval, for the generic legal framing, for
the mis-described posture, and for treating the strongest escalation rung as
worth a five-point adjustment. The number is graded on soundness given the
outcome, not on being wrong: an equally thin analysis that landed on `granted`
would score about the same.

## Leakage

Mode `forward`. The prediction ran 2026-09-01 against a snapshot ending at the
Aug 31 government response; the disposition did not exist until Sept 4. The
log's 26 calls are all `unobserved` (`result_capture_coverage` 0.0 — this
engine's standing shape, not a defect), so each is graded on its query: reads
of the provisioned inputs and the statpack, one CourtListener `dockets`
endpoint call and two searches on the caption / CA4 number, two `validate`
runs, and the output writes. No query reaches past the event date and no
`retrieved_doc_date` is legible. The reasoning reads the posture as pending.
`retrieved_outcome_material` = false, `influenced_prediction` =
`not_applicable`, `leakage_suspected` = false. No evidence a decided case was
provisioned forward.

## Big-case read

My own read is 0.7 (see `big_case.notes`). The candidate's rationale and score
sat in the same `prediction.json` I read for the headline fields, so I cannot
claim I formed the read before seeing theirs; the basis recorded is my own,
formed from the docket, the disposition, and the stakes described above.
