# Evaluation — codex-baseline, scotus/9526000274, evt-brief-response-disposition

**Stage: interim** (emergency stay application 26A274, forecast at the
response-filed moment). Outcome: `granted`, `actual_granted = 1`, resolved
2026-09-04; the outcome's `interim_signals` record a referral to the Court and
one amicus brief.

## Scores

- `correct = 1`: `predicted_disposition` `granted` matches `actual_disposition`
  `granted` on the label.
- `brier_score = (0.74 − 1)² = 0.0676`.
- `segment_base_rate`, `brier_skill_score`, `base_rate_basis`: not written.
  On an interim cell the baseline and the skill are the harness's —
  `stamp-cell` pools the statpack's resolved substantive slice over
  application-Terms strictly before 2026 and writes both, clearing them if the
  pool is under the 50-resolved floor. For the reader: the committed pack's
  strictly-prior rows are OT2025 (17/226) and OT2024 (14/70), a 31/296 ≈ 10.5%
  pool that clears the floor, so a non-null stamp is what I expect; if it
  comes back null, the pack in force at the stamp differed from the one I
  read. `base_rate_basis` stays null structurally — an application freezes no
  band (this prediction's `context.band` is null, the ordinary interim shape,
  no flag).
- `vote_accuracy`, `judgment_correct`, `semantic_grades`: omitted / null —
  none applies off the merits stage. `claim_scores` is the harness's
  (`interim-v1`).

## Reasoning quality: 0.80

What drove the grade, on `reasoning.md` alone:

- **Baseline handled correctly.** Reads the interim section's strictly-prior
  rows, gets 31/296 ≈ 10.5%, and notes it clears the floor before adjusting.
- **Grounded in primary material.** The candidate pulled the Fourth Circuit's
  2026-08-25 opinion and Judge Wilkinson's dissent through CourtListener and
  reasons from what they actually hold: the constructive-denial jurisdictional
  route, the finality objection, and the dissent's *NRSC v. FEC* argument. It
  correctly identifies the jurisdictional hook as the applicants' cleanest
  path to a stay, which is also how the application itself is framed (the
  record's application text leads with the two jurisdictional bars).
- **Discipline about what it had not read.** It declines to assume the
  government's position from the fast filing alone, names the unavailable
  application and response text as the main uncertainty, and gives the
  denial case a fair paragraph (monetary harm, disturbing a lower-court
  judgment). That is the right epistemic posture for a cell that could not
  read the filings.
- **Where it is weaker.** The step from 10.5% to 0.74 is argued qualitatively
  (ladder rung, Chief Justice, election timing, divided panel) without saying
  how much each contributes, and the government-alignment factor — the
  strongest single reason to expect a grant here, given that the FCC and
  United States were respondents defending the notice below — is left
  implicit. The corpus query is candidly described as a small check rather
  than a conditioned rate, which is honest but means the ladder signals do no
  quantitative work.

Net: a sound, well-sourced analysis that reached the right answer for the
right reasons while stating its blind spots; a modest deduction for the
under-argued magnitude of the adjustment.

## Leakage: forward, not applicable

`retrieval_log.json` records `mode: forward`, 57 calls, result-capture
coverage 0.53 (the engine's shell wrapper is captured, the inner calls are
not — a standing shape). Every CourtListener call targets the Fourth Circuit
docket/opinion or *NRSC v. FEC*; the newest `retrieved_doc_date` is
2026-08-31 (the corpus query). Nothing queries this application's own
disposition, which did not exist until 2026-09-04, three days after the
prediction. The forward default holds and I confirmed rather than
rubber-stamped it: no sign of a decided case provisioned forward.
`retrieved_outcome_material = false`, `influenced_prediction =
not_applicable`, `leakage_suspected = false`.

## Big case (independent read): 0.70

Formed from the record's application text and the outcome; see the JSON
notes. High political and financial stakes in the run-up to the midterms,
resting on a narrow jurisdictional question — significant emergency-docket
matter, not a landmark. The candidates' own scores were visible in the staged
`prediction.json` and are not the basis of this read.
