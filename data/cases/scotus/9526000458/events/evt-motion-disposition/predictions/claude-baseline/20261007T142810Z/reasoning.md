# Rationale for the numbers

**Cell.** Forward interim cell, `moment: arrival`, application Term 2026.
Baseline snapshot `2026-10-03.json` (arrival-position cut at the October 2
submission entry). `record/context.json`: `band: null`, `response_requested:
false`, `referred_to_court: false`, `amicus_briefs: 0`, `signals_observable:
true`. Band null is the normal interim state, so no cert band table and no
caption-class floor were used. The provisioned `application.txt` (134 pages,
`truncated: true`, `empty_text: false`) was readable through the conclusion
and into the appendix; I read the introduction, statement, argument, and the
cert-before-judgment section.

## Anchor

`metrics/statpack.md`, *The interim docket (applications)*. The caption says
the rows ground the interim stage's scored base rate (not the older
descriptive-only wording). Pool for Term 2026 is Terms 2016–2025 strictly
before mine; only 2024 and 2025 carry parsed substantive rows:

| Term | resolved (subst.) | granted | unparsed |
| --- | --: | --: | --: |
| 2025 | 226 | 17 | 0 |
| 2024 | 70 | 14 | 972 |
| pooled | 296 | 31 | — |

Pooled rate 31/296 ≈ 10.5%, well above the 50-resolved floor, so a published
baseline exists and that is the yardstick I am scored against. Caveats I
carry: Term 2024 is mostly unparsed, so the pool leans on one Term; the rate
is unconditioned on the escalation ladder while this cell was selected on it;
and the pooled population is dominated by applications filed by the federal
government, which drives much of the grant count.

## Adjustments

**Up from the anchor** (toward ~0.30 for any relief):

- *Mirabelli v. Bonta* (25A810, March 2, 2026, per curiam) is a near-direct
  analogue: private parents, Ninth Circuit, parental-rights claim about a
  child's wellbeing, Kagan as Circuit Justice, response requested, referred,
  granted (as to parents) 6–3 with a Barrett concurrence joined by the Chief
  Justice and Kavanaugh calling the result "dictated by existing law". The
  application leans on it heavily and frames the Ninth Circuit as cabining it
  again, which is the posture that drew the Court's intervention last time.
- Six Justices joined *B.P.J.* (June 30, 2026) and its "reality of sports"
  language about safety risks in contact sports; the lead fact here (an
  alleged sexual assault during a wrestling match against a male opponent)
  speaks directly to it, and the relief sought (opt-out without penalty, with
  notice) is narrow and easy to write for one student.
- Experienced counsel of record (ADF, John Bursch) and a response requested
  within four days.

**Down from there** (to 0.20 for an unqualified grant):

- Posture is the hardest on the emergency docket: both courts below denied a
  *preliminary* injunction, so the Court would have to enter relief no court
  has entered, on a record the district court and Ninth Circuit called
  factually disputed, with a Spending Clause clear-notice holding in the way.
  Mirabelli, by contrast, restored a permanent injunction entered after full
  summary judgment. In 2023 the Court declined to disturb the status quo in
  the B.P.J. application (22A800) over an Alito/Thomas dissent.
- The Title IX theory asks the Court to extend B.P.J. from "a State may
  exclude" to "a State must exclude" without plenary briefing; the Court is
  unlikely to do that on an application, and the parental-rights hook is
  narrower than the Mirabelli facts (the District has offered forfeits, and
  the Ninth Circuit read the notice request as reaching other students'
  information).
- The resolver collapses mixed orders to denial. The likeliest grant here is
  partial (one claim, not the other; the injunction but not certiorari before
  judgment), exactly the shape Mirabelli's own order took ("granted as to
  the parents but is otherwise denied"). That takes P(unqualified grant)
  meaningfully below P(any relief).

Net: **P(unqualified grant) = 0.20**, roughly double the pooled anchor.

## The three increments

- `response-requested-increment` 0.98: forward mode permits reading this
  docket's later entries, and the live docket shows Justice Kagan requested a
  response on October 6 (due October 13); the sibling event directory for the
  response-requested moment exists in the case folder too. From my frozen
  state (`response_requested: false`) the claim has effectively resolved; the
  residual reflects only resolver or parse risk. Disclosed in `flags.json`.
- `referral-increment` 0.85: contested, salient application with a response
  requested; Kagan referred in Mirabelli and a single-Justice denial would be
  renewed. The pack's referred count (178 of 367 substantive) is a right-
  censored shape, not a conditioned rate, and I used it only as shape.
- `amicus-increment` 0.75: 22A800 drew three amicus entries within four days
  of a response request on the same subject; this application has a similar
  constituency, but the window is one week and amicus filings on applications
  are not routine, so not higher.

## Uncertainty and where to discount me

- The biggest swing is whether the Court sees this as a Mirabelli sequel
  (grant) or a fact-bound preliminary-injunction denial (deny). I lean deny
  because of posture, but a 0.30–0.35 unqualified-grant number is defensible.
- The anchor rests almost entirely on Term 2025's parse coverage, and that
  Term's grants are largely federal-government applications; a private-
  applicant base rate would be lower than 10.5%.
- No merits-brief or response text exists yet; the respondents' arguments are
  known only as the application characterizes the lower-court orders.
- Corpus priors: `fedcourts query --include-applications` returned mostly
  time-extension grants under `--disposition granted` and recent cert denials
  otherwise, so it contributed no interim-specific priors; the anchor is the
  statpack alone.
- B.P.J.'s opinion text was not available on CourtListener; I confirmed its
  disposition and lineup from the Court's docket and relied on the
  application's quotations for its reasoning.
