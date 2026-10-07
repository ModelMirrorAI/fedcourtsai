# Evaluation — gemini-baseline — scotus/9526000449 / evt-motion-disposition

## The cell

This is an **interim** cell (`event.yaml` `stage: interim`, `moment: arrival`):
application 26A449, *Elisha Holloway v. Bryan Polk*, an emergency application
for a stay pending certiorari submitted to Justice Alito on 2026-09-27. The
outcome is **denied** by Justice Alito on 2026-10-05, `actual_granted = 0`, with
every interim signal at its floor (no response requested, no referral, no
amicus). The candidate ran **forward** on 2026-10-03 against a 2026-09-28
snapshot (arrival-position cut, anchor 0), two days before the denial.

## Scores

- `correct = 1`: `predicted_disposition: denied` matches `actual_disposition:
  denied`.
- `brier_score = (0.001 - 0)^2 = 0.000001`.
- `segment_base_rate` and `brier_skill_score` are **not written**: on an interim
  cell both are the harness's. `stamp-cell` pools the substantive slice over
  application-Terms strictly before this cell's Term 2026 and writes the rate and
  the skill, clearing both where the pool is under its 50-resolution floor.
  `base_rate_basis` stays null structurally (an application freezes no band, and
  the candidate's `context.band` is null, so no cert-band flag applies). For the
  reader of the stamped number: the committed `metrics/statpack.md` interim table
  carries parsed substantive resolutions only for OT2025 (226 resolved, 17
  granted) and OT2024 (70 resolved, 14 granted) inside the eligible window, so
  the pool the stamp should see is 31/296, about 10.5%, and clears the floor. If
  the stamped field comes back null, the pack has changed since this run.
- `vote_accuracy` omitted (not a merits stage). No `semantic_grades` (no semantic
  set is declared off merits). `claim_scores` is the harness's.

## Reasoning quality: 0.45

What the rationale gets right: it identifies the application as pro se, from a
Texas state civil matter, submitted to a single Circuit Justice with no
escalation signal, and it reads the committed statpack correctly (pooled 10.47%
over the prior-Term substantive slice, floor cleared). The directional call,
that a pro se stay application from a state civil case is almost never granted
and will be denied by the Circuit Justice without a response or referral, is the
right one and the outcome bore it out at every rung.

What holds the score down:

- **The key factual claim rests on an unobserved result.** The rationale says the
  applicant "has been recommended for designation as a vexatious litigant in
  federal court," attributed to a web search. The log records the search but no
  result (capture coverage 0.0 for this engine), and nothing else in the cell
  corroborates a vexatious-litigant designation. The claim is stated as fact and
  does real work in the argument ("the underlying claims appear frivolous"). A
  sound rationale distinguishes what it read from what it inferred.
- **The number is more extreme than the argument supports.** 0.001 is below any
  plausible order-form or classification noise floor for an interim resolver,
  and the rationale offers no account of residual risk at all. The outcome
  rewards the extremity here, but the reasoning does not earn it: the step from
  "uniformly denied absent extraordinary circumstances" to one-in-a-thousand is
  asserted, not argued.
- **Thin engagement with the standard.** There is no mention of what a stay
  pending certiorari of a state judgment requires (reasonable probability of a
  cert grant, fair prospect of reversal, irreparable harm), which is the
  framework that makes the denial predictable rather than merely customary.
- **The subject matter was unknown and the rationale does not say so clearly.**
  The application text was empty at prediction time (`empty_text: true`, as the
  rationale notes); the record now carries an OCR body showing a child-custody
  conservatorship and attachment matter with a fee-based appellate dismissal
  below. "Civil dispute" is not wrong, but the rationale treats the gap as
  immaterial rather than as a bound on what it could say.

The rationale is short, directionally correct, and base-rate-aware, but its one
case-specific fact is unverified and its probability is unexplained. That is a
below-median rationale that happened to land on the best Brier of the three.

## Leakage: not applicable (forward)

Mode `forward`; the application was genuinely pending when the prediction was
made (created 2026-10-03, denied 2026-10-05). I scanned for this case's own
disposition surfacing as decided: no `retrieved_doc_date` on or after 2026-10-05,
no query for this docket's result (the one corpus query, `--disposition denied`,
is a generic shape query with no case key; the one web search names the parties
and the Texas Supreme Court, predates the denial, and its result is unobserved so
is graded on its query), and the reasoning reads the pending state off the
snapshot rather than any result. No `data/qp-topics/` read. The candidate's
`flags.json` is not staged, so its absence proves nothing; the `not_applicable`
grade rests on the log and the timing. `retrieved_outcome_material = false`,
`influenced_prediction = not_applicable`, `leakage_suspected = false`.

## Big case: 0.03

Formed before reading the candidate's score. A pro se individual-versus-
individual emergency stay in a Texas family-law matter, denied in one line by
the Circuit Justice with no response, referral, or amicus. The stakes to the
applicant are personal and high (custody of children), but the institutional
and doctrinal significance is negligible.
