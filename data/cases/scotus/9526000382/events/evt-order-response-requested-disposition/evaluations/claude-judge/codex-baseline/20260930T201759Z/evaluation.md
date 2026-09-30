# Evaluation of codex-baseline — 26A382, Strulovitch v. Bain (interim, response-requested)

## The cell and the outcome

This is an **interim** cell (`event.yaml` stage `interim`), graded **forward**:
the prediction was created 2026-09-27 against a 2026-09-23 snapshot, and the
application was decided 2026-09-29. The disposing entry reads: "Order entered by
Justice Sotomayor: Upon consideration of the application of counsel for the
applicants and the response filed thereto, it is ordered that the application
for stay is denied without prejudice to applicants again seeking relief, if
necessary, once state court remedies are exhausted." `outcome.json` records
`actual_disposition: denied`, `actual_granted: 0`, with ending signals
`response_requested: true`, `referred_to_court: false`, `amicus_briefs: 1`
(the Becket Fund brief docketed 2026-09-25). The response was filed 2026-09-28.

## Scores

- `correct` = 1: `predicted_disposition` `denied` matches `actual_disposition`
  `denied` exactly.
- `brier_score` = (0.40 − 0)² = 0.16, written per the definition; the harness
  re-stamps it on an interim cell.
- `segment_base_rate`, `brier_skill_score`, and `base_rate_basis` are left
  null: on an interim cell the baseline and the skill are the harness's,
  pooled by `stamp-cell` from the statpack's interim section over
  application-Terms strictly before 2026. For a reader of the stamped number:
  the committed pack's strictly-prior rows with parsed substantive resolutions
  are Terms 2025 (226 resolved, 17 granted) and 2024 (70 resolved, 14 granted),
  296 resolved in all, which clears the registered floor of 50, so a null stamp
  here would not be a thin-pool refusal on the pack as committed. That is a
  description of the pack, not a rate I am recording; the prediction froze no
  band (`context.band: null`), so there is no cert-band anomaly to flag.
- `vote_accuracy`, `judgment_correct`: null. No votes are scored off the merits
  stage, and no judgment exists on an interim cell.
- No `semantic_grades` block: no semantic set is declared on an interim event.
- `claim_scores`: not mine; the harness computes the `interim-v1` block.

## Reasoning quality: 0.70

Graded on `reasoning.md` alone. The document is disciplined about what it knows
and does not know, and its legal framing is sound; its weakness is that the
number does not follow from the analysis.

What it got right:

- **The information boundary is stated precisely**: forward mode, the
  2026-09-24 cutoff, the fact that the response was not yet due and that its
  absence proves nothing, and that every description of the lower-court orders
  comes from the applicants' own submission. Few predictors say this plainly.
- **The base rate is pooled correctly** (31/296, 10.47%, floor cleared) with the
  right caveats: unweighted machine-resolved pool, uneven parse coverage, and,
  importantly, that the forecast population is selected on escalation so
  moving above the pool is not itself evidence of skill.
- **Posture is named as the major counterweight**, in the right terms: reliance
  on potential appellate jurisdiction and prolonged inaction rather than a final
  judgment, an undecided but fully briefed Appellate Division motion, and no
  fixed deadline that forecloses later relief. The candidate also refused to
  accept the applicants' Yeshiva distinction as verified. The order that issued
  rested on exactly this ground.
- **The equities are read from both sides.** Bain's interest in access to a
  civil forum and in not being pressured by a censure is taken seriously, and
  the candidate declines to assume a party-specific injunction fails neutrality
  analysis just because the applicants call it a rule of one. That is a fair
  reading of a contested record.
- Nken is checked at the source for the stay factors, with the caveat that it
  does not supply jurisdiction here.

What holds it down:

- **The 40% is not earned by the reasoning that precedes it.** The document
  concedes the pool is 10.5%, that escalation-selection is not skill, that
  posture is the major counterweight, that the equities are not one-sided, and
  that the applicants' account is unverified; it then nearly quadruples the
  pool on the strength of the response request and the compelled-withdrawal
  directive, and calls the move "a judgmental adjustment, not a fitted
  estimate." A well-argued 20 to 25% would have followed from this text; 40%
  reads as hedging toward the merits appeal the prose had just discounted.
- It does not engage the Court's actual practice on stays directed at state
  interlocutory orders (Yeshiva's exhaustion logic, the Malliotakis contrast)
  beyond noting that the applicants tried to distinguish Yeshiva. Its search
  for the Yeshiva order failed, and it honestly says so, but the gap is real:
  the decisive doctrine is described only through the applicants' brief.
- It does not price the resolver's denial-first treatment of a partial stay as
  a reason the unqualified-grant number should sit lower, though it mentions
  that a narrower stay is a material alternative.

The reasoning would have read as sound, if under-committed, had the stay been
granted. It is careful work whose headline number is its weakest part.

## Leakage

Forward cell, confirmed. The prediction predates the disposition by two days.
Of 34 logged calls, three hosted web searches are `unobserved` and so are
graded on their queries: all three seek the 2022 Yeshiva University order and
none concerns this application. The CourtListener calls searched for the
Yeshiva opinion (no result) and read Nken v. Holder. Every other call reads the
prompt, the schemas, the provisioned record, or the committed statpack. The
candidate states it did not retrieve this application's docket, history, or
outcome; the log agrees. `retrieved_outcome_material: false`,
`influenced_prediction: not_applicable`, `leakage_suspected: false`. Nothing
suggests a decided case was provisioned forward.

## Big case

My independent read is 0.35 (see `big_case.notes`): a genuinely novel
church-autonomy and compelled-speech question with serious counsel and an
institutional amicus, but a private ownership dispute, interim relief, and a
disposition by the Circuit Justice alone on exhaustion grounds with no noted
dissent. The candidate's own 0.60 was read only after that number was set.

## Flags

None. No `flags.json` written for this cell.
