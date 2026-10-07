# Evaluation — codex-baseline — scotus/9526000449 / evt-motion-disposition

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
- `brier_score = (0.06 - 0)^2 = 0.0036`.
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

## Reasoning quality: 0.62

This is the most methodologically disciplined of the three rationales, and the
least willing to use the signal it had.

Strengths:

- **Correct and carefully caveated baseline.** It pools 31/296 (10.47%) over
  OT2024 and OT2025, excludes the current Term, notes that OT2016 to OT2023 are
  unparsed rather than zero, quotes the coverage asymmetry (972 unparsed in
  OT2024 against none in OT2025), and repeats the pack's caveats about
  withdrawals, mixed dispositions, right-censored escalation columns, and the
  scored population sitting higher on the ladder than the pooled one. Nothing
  here is misread.
- **Honest about the evidentiary state.** It says plainly that the application
  text was empty, that this is unavailable content rather than an inadequate
  filing, that the snapshot's docketed date post-dates its label, and that no
  outside authority was recovered. It separates inference (self-representation
  from the counsel-of-record field) from fact.
- **Principled about what is and is not adverse evidence.** "Unreadable advocacy
  is not adverse evidence on the merits, and no response at the opening entry is
  not an adverse later development" is exactly right as far as it goes.

Weaknesses:

- **Under-uses the signal it acknowledges.** Pro se applicant, individual
  respondent, state-court origin, single-Justice stage: the rationale names each
  of these and then moves the number from 10.5% only to 6%. Those observables
  place the application in the stratum of the interim docket that is denied
  essentially always, and the rationale's own description of the pooled cohort
  (dominated by counseled, often governmental, often referred applications)
  explains why the pooled rate is the wrong anchor for this one. Declining to
  adjust further because the text was unreadable confuses two things: the
  text's absence is not adverse evidence, but the caption and posture are, and
  they were legible.
- **No engagement with the stay standard.** It searched for the Hollingsworth
  factors and got nothing, then wrote the forecast without them. The requirement
  of a reasonable probability of a cert grant on a federal question is what makes
  a pro se stay from a state civil judgment a near-certain denial, and the
  rationale never applies it.
- **The ladder forecasts sit high for the shape described.** A 22% referral
  probability on an unopposed pro se application the rationale itself expects
  to be handled by a short single-Justice denial is in tension with its own
  modal story. (The ladder claims are scored in code and do not enter this
  number; I note the tension only as a coherence point about the rationale.)

The result is a rationale that would read well on a counseled, referred
application and under-commits on this one. Sound, transparent, and
systematically too cautious: a Brier thirty-six times worse than the next
candidate's, with the same directional call and more of the pack read correctly.

## Leakage: not applicable (forward)

Mode `forward`; the application was genuinely pending when the prediction was
made (created 2026-10-03, denied 2026-10-05). I scanned for this case's own
disposition surfacing as decided: no `retrieved_doc_date` on or after 2026-10-05,
no query for this docket's current state. The two web calls (a search for the
Hollingsworth stay standard and an open of the pre-decision application PDF
named in the provisioned manifest) are unobserved and so graded on their
queries, neither of which seeks a result; the one CourtListener call was a
citation lookup that returned HTTP 429. The prose states that no disposition,
subsequent history, or current docket was requested. No `data/qp-topics/` read.
The candidate's `flags.json` is not staged, so its absence proves nothing; the
grade rests on the log and the timing. `retrieved_outcome_material = false`,
`influenced_prediction = not_applicable`, `leakage_suspected = false`.

## Big case: 0.03

Formed before reading the candidate's score (which it left null with a reason;
that is a legitimate choice and not penalized here). A pro se individual-versus-
individual emergency stay in a Texas family-law matter, denied in one line by
the Circuit Justice with no response, referral, or amicus. The stakes to the
applicant are personal and high (custody of children), but the institutional
and doctrinal significance is negligible.
