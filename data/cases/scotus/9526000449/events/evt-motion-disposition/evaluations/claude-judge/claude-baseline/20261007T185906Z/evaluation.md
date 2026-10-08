# Evaluation — claude-baseline — scotus/9526000449 / evt-motion-disposition

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
- `brier_score = (0.01 - 0)^2 = 0.0001`.
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

## Reasoning quality: 0.78

The strongest rationale of the three: it reads the baseline correctly, says
why the baseline is the wrong anchor for this application, grounds that
argument in observables it actually retrieved, applies the legal standard, and
prices its own residual uncertainty.

Strengths:

- **Baseline read correctly and situated.** 31/296, about 10.5%, over OT2024 and
  OT2025 with OT2016 to OT2023 noted as unparsed; the 7.5% versus 20% spread
  attributed to coverage as much as behaviour, with the 972 unparsed OT2024
  applications cited.
- **The adjustment is argued, not asserted.** The rationale explains that the
  pooled cohort is dominated by counseled and governmental applications (citing
  the section's 178 referrals and 64 response requests over 367 substantive
  applications) and then places this application at the opposite end of every
  observable: pro se, individual respondent, state civil origin, no escalation
  signal. Each observable was legible from the snapshot or from captured
  retrieval.
- **Case-specific retrieval that was captured and used proportionately.** The
  RECAP and opinion searches (results captured, dates 1999 to 2025) established
  the applicant as a repeat self-represented litigant with a pending N.D. Tex.
  *Holloway v. Polk* civil-rights suit and several Texas appellate matters. The
  rationale takes from that only the litigant class and says so, and declines
  to fetch further after the CourtListener throttle rather than waiting.
- **The stay standard is applied.** A stay of a state judgment needs a
  reasonable probability of a cert grant plus a fair prospect of reversal on a
  federal question; the rationale names this and explains why nothing visible
  meets it.
- **Residual risk is priced.** 0.01 is explicitly the order-entry and
  classification noise floor, with withdrawn and dismissed counted as ungranted.
  That is the right way to arrive at a low number.
- **The ladder story is coherent.** Referral priced above the other rungs for
  stated mechanical reasons (renewed applications docketed on the same number;
  some Justices refer so the denial issues from the full Court), with the
  disposition claim and the ladder claims moving together. (Ladder claims are
  scored in code and do not enter this number.)

Weaknesses:

- **The subject-matter guess was wrong, though caveated.** The rationale
  speculates the dispute is "landlord-tenant or civil-rights," reading from the
  applicant's other matters. The record now carries an OCR body showing a
  child-custody conservatorship modification and writ of attachment, with the
  appeal dismissed below for nonpayment of a $205 fee while an indigency
  reconsideration was pending. The rationale does flag that it did not know
  the Texas judgment at issue and that the gap bounds *why* rather than
  *whether*, and that is fair, but a family-law custody matter with an
  M.L.B.-shaped access question is a slightly more sympathetic posture than the
  rationale imagined. The denial shows it did not change the answer.
- **One line of the retrieval was spent on another cell's committed output**
  (a different docket's prediction, read for ladder calibration). It is not
  leakage and not forbidden, but it is calibration against a prior forecast
  rather than against the record.

Correct direction, best-argued adjustment, second-best Brier, and transparent
about every gap. The subject-matter miss and the reliance on an inferred
litigant profile keep it short of the top of the range.

## Leakage: not applicable (forward)

Mode `forward`; the application was genuinely pending when the prediction was
made (created 2026-10-03, denied 2026-10-05). I scanned for this case's own
disposition surfacing as decided: the captured `retrieved_doc_date` values run
from 1999 to 2025, all before the denial; the RECAP search for docket 26A449
returned nothing; the corpus query over recent applications was a shape check
on the Term's stream and not keyed on this case; the reads of another case's
committed prediction concern a different docket. The prose states that no call
sought or surfaced this application's disposition, and the log agrees. No
`data/qp-topics/` read. The candidate's `flags.json` is not staged, so its
absence proves nothing; the grade rests on the log and the timing.
`retrieved_outcome_material = false`, `influenced_prediction = not_applicable`,
`leakage_suspected = false`.

## Big case: 0.03

Formed before reading the candidate's score. A pro se individual-versus-
individual emergency stay in a Texas family-law matter, denied in one line by
the Circuit Justice with no response, referral, or amicus. The stakes to the
applicant are personal and high (custody of children), but the institutional
and doctrinal significance is negligible.
