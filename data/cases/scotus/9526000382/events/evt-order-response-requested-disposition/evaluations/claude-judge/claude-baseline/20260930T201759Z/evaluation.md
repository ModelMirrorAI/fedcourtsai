# Evaluation of claude-baseline — 26A382, Strulovitch v. Bain (interim, response-requested)

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
- `brier_score` = (0.22 − 0)² = 0.0484, written per the definition; the harness
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

## Reasoning quality: 0.85

Graded on `reasoning.md` alone. This is the most complete analysis of the three
and the one whose stated mechanism matched the order that issued.

What it got right:

- **It identified the dispositive problem and the Court's own rule for it.**
  The reasoning contrasts Malliotakis (both New York appellate courts had
  refused a stay, so section 1257 jurisdiction attached) with this record
  (one Appellate Division justice denied interim relief, the panel's stay motion
  is undecided, no Court of Appeals application), and reads the 2022 Yeshiva
  majority as denying precisely because state interim avenues had not been
  pressed, telling applicants to return only if they sought and received
  neither. The order that issued denied "without prejudice ... once state court
  remedies are exhausted," which is that rule applied.
- **It treated the applicant's exhaustion argument as an argument, not a
  fact.** The application says exhaustion is complete because New York gives no
  route to challenge Appellate Division inaction; the reasoning notes the
  appeal itself was not shown to be expedited and that the swing Justices can
  plausibly say the state courts have not yet refused. That is the right
  skeptical posture toward a one-sided record.
- **The base rate is pooled correctly** (31/296 over strictly-prior Terms,
  10.5%, floor cleared) and its fragility is named (one fully parsed Term
  carries the pool; the escalation columns are right-censored and unconditioned).
- **It priced the resolver's denial-first rule**: a stay confined to the
  seruv-withdrawal directive is the most plausible grant-shaped outcome and
  resolves as ungranted, which correctly shaves the unqualified-grant number.
- **It named mootness** (a Second Department ruling before the Court acts).
- **Its forward retrieval was disclosed in the prose** (the Becket amicus filed
  after the snapshot cutoff), which is the honest shape.

What holds it below the top of the range:

- The upward adjustments lean on very thin comparators: "the two September
  grants (26A308, 26A388) both carrying a requested response and a referral"
  is two observations, acknowledged as shape only but still doing real work in
  moving 10.5% to 22%.
- Having concluded that the exhaustion problem is judged "against the Yeshiva
  majority's stated rule," the reasoning still lands at 22%, roughly double the
  pool. The document does not say why that rule, if it governs, leaves a
  one-in-five chance of an unqualified grant rather than a smaller one. The
  number is defensible; the bridge from the analysis to it is not fully argued.
- The Malliotakis weight rests on a concurrence's account of procedural history,
  as the candidate itself notes.

None of these is an error of law or fact on the record I hold. The analysis
would have read as sound had the stay been granted, which is the test.

## Leakage

Forward cell, confirmed rather than rubber-stamped. The prediction predates the
disposition by two days. The log (41 calls, all captured) shows one
case-specific fetch past the baseline, the live 26A382 docket with a
`retrieved_doc_date` of 2026-09-25 (the amicus entry), plus searches for
coverage of this application; none surfaces the 2026-09-29 order, which did not
yet exist. The remaining web and CourtListener calls concern comparator cases
and the lower-court history. One shell command excludes the `data/qp-topics/`
path from a `git status` listing; that is a filter on the listing, not a read of
the path. `retrieved_outcome_material: false`, `influenced_prediction:
not_applicable`, `leakage_suspected: false`. Nothing suggests a decided case was
provisioned forward.

## Big case

My independent read is 0.35 (see `big_case.notes`): a genuinely novel
church-autonomy and compelled-speech question with serious counsel and an
institutional amicus, but a private ownership dispute, interim relief, and a
disposition by the Circuit Justice alone on exhaustion grounds with no noted
dissent. The candidate's own 0.40 was read only after that number was set.

## Flags

None. No `flags.json` written for this cell.
