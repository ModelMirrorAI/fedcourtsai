# Evaluation: codex-baseline — scotus/9526000273, evt-motion-disposition

## Stage and outcome

This is an **interim** cell: application 26A273, a stay of execution pending
certiorari (linked petition 26-5211), submitted to Justice Thomas on
2026-08-28. The outcome is `actual_disposition = withdrawn`,
`actual_granted = 0`, resolved 2026-09-25: the applicant filed a letter
withdrawing the application after the scheduled 2026-09-16 execution date
had passed, and the Court entered "Application (26A273) withdrawn." No order
on the merits of the application was ever entered, no response was
requested, no referral to the Court was docketed, and no amicus brief was
filed.

Because the cell is interim, `segment_base_rate` and `brier_skill_score` are
the harness's: `stamp-cell` pools the statpack's substantive-application
slice over application-Terms strictly before OT2026 and writes both, or
clears them where the pool is under the 50-resolved floor. I wrote neither
and left `base_rate_basis` null. For the reader's orientation only, the
committed `metrics/statpack.md` interim section shows OT2025 17/226 and
OT2024 14/70, so the strictly-prior pool the stamp will read is 31/296
(about 10.5%), which clears the floor; if the stamped rate comes back null
anyway, the pack rather than the pool is the reason. `claim_scores` (the
`interim-v1` set) is likewise the harness's and I did not touch it.

## Scores

- `correct = 0`. The prediction named `denied`; the outcome label is
  `withdrawn`. Exact match on the label is the rule, and no candidate could
  have named a withdrawal, so this bit says nothing about relative skill on
  this cell (see the flag).
- `brier_score = 0.0064`: probability 0.08 against `actual_granted = 0`. A
  withdrawn application counts as ungranted under the statpack's standing
  rule, so the binary is meaningful even though the label match is not.
- `vote_accuracy` omitted (not a merits cell). No `semantic_grades` block
  (no semantic set is declared on an interim event).

## Reasoning quality: 0.80

What the rationale does well, judged on `reasoning.md` alone:

- It reads the interim baseline correctly (31/296, 10.5%), and states the
  right caveats about it: the resolved slice is selected for parseable
  dispositions, OT2024 coverage is uneven, and the prediction reserve sits
  higher on the escalation ladder than the pooled cohort.
- It engages the actual legal dispute rather than the category. It
  identifies the Georgia quorum statute, the preservation and vehicle
  objections (state-law litigation below, federal theories surfacing in the
  petition), the Eleventh Circuit's narrow reading of *Woodard* in
  *Gissendaner*, and the June 2026 *Pizzuto v. Valley* opinion as a recent
  rejection of a closely related clemency claim. Those authorities were
  retrieved with a pre-2026-09-01 date filter and are the right ones.
- Two factual claims I checked against the provisioned application text
  hold: the state court did retreat to a "mere quorum" ruling, and the
  application does report that respondents' waiver of a response on the
  linked petition was not accepted by the Court. Treating the latter as a
  signal of Court attention is a fair inference, and the rationale weighs
  it against the vehicle problems rather than letting it dominate.
- It disclosed its own conditioning problem (no `opened_at`, `as-stored`
  snapshot including the 2026-08-31 response) and said how it handled it.

Where it falls short:

- It did not consider non-merits resolutions at all. Withdrawal, mootness
  from a state-court stay, or a clemency grant are live routes for a
  capital application whose clemency hearing is itself the subject of the
  dispute, and the rationale forecasts as if denial and grant exhaust the
  space. The 94% referral figure in particular presupposes the Court would
  act on the application.
- The 8% headline is the highest of the three and sits close to the pooled
  rate despite the rationale's own finding that the capital-stay class is
  weaker than the pool. The equities paragraph justifies not going to a
  token value, but the number lands a little above where the stated
  reasons point.

## Leakage

Forward cell, `influenced_prediction = not_applicable`,
`retrieved_outcome_material = false`, `leakage_suspected = false`. The
prediction was created 2026-09-01; the application was still pending until
2026-09-25, so there was no disposition to retrieve. Everything the
candidate says it fetched (the two supremecourt.gov filings dated
2026-08-28 and 2026-08-31, and opinions filed before 2026-09-01) predates
prediction time, and the reasoning presupposes a pending application.

One thing to record: the harness-captured log for this candidate is thin.
It holds 14 rows, all `shell` or `other` (each shell command appears twice,
once as the wrapper and once as the inner command), coverage 0.57, and
ends at 02:49:21Z, about a minute before the prediction's `created_at`. It
carries none of the MCP searches or PDF fetches the candidate's
`retrieval.md` discloses in detail (with query ids and document ids). So
the leakage grade here rests on the candidate's disclosure and the dates it
gives, not on an independent log of those calls. That weakens the evidence
without changing the answer, since the outcome did not exist to be found.
One `other` row carries a `[redacted:fernet-token]` marker: that is the
harness redacting a credential-shaped run at capture, not outcome material.

## Big case

My own read is 0.25 (see `big_case.notes`). Disclosure: the predictor's
`big_case_score` sits in the staged `prediction.json`, which I read before
writing this, so the read is independent in its reasons but was not formed
without exposure to their number.
