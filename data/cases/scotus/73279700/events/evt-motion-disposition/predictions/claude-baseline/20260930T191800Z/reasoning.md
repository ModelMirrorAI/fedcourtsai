# Rationale for the numbers

**Cell.** Interim stage, `moment: arrival`, `mode: forward`. Snapshot
`record/snapshots/2025-11-19.json`, cut at `arrival-position` (anchor index 0). The
snapshot carries a single docket entry: "Application (25A622) for a stay, submitted to
Justice Kagan" on Nov 18 2025. Context: `band: null` (normal for an interim cell, so no
cert-band anchoring and no caption-class floor), `response_requested: false`,
`referred_to_court: false`, `amicus_briefs: 0`, `term: 2025`. No `record/documents/`
directory was provisioned, so I have no filed-document text — the forecast rests on the
caption, the docket entry, priors, and base rates.

**What the record shows.** The applicant, Allen Watkins, is listed as his own attorney
of record with no counsel, i.e. pro se. The respondent is the United States District
Court for the District of Arizona and the lower court is the Ninth Circuit
(No. 25-2374). A caption naming the district court as the adverse party is the
signature of a mandamus petition denied by the court of appeals; the applicant now
seeks a stay from the Circuit Justice for the Ninth Circuit. Bottom of the escalation
ladder: no response requested, no referral, no amici.

## Anchor

The statpack's "The interim docket (applications)" section carries the scored base
rate. This application's Term is 2025, so the pool is application-Terms 2015–2024
strictly before it. Only Term 2024 has any parsed substantive rows: 70 resolved, 14
granted, 20.0%. That pool (n=70) clears the pre-registered floor of 50, so a published
baseline exists and I anchor on **20.0%**. The section's caption already describes the
rate as the scored base rate rather than descriptive-only, so I read the current
caption. Two heavy caveats from the section itself: Term 2024 has 972 of 1,297
applications unparsed, so the pool rests on a partially covered Term; and the published
cohort is not the predicted population, which is selected up the escalation ladder.
Both caveats cut toward the pooled 20% being an over-statement for an application at
rung zero.

## Adjustments

- **Pro se applicant (strong, downward).** In the 400 most recent corpus rows I
  pulled with `fedcourts query --include-applications`, 70 were substantive
  applications; the 16 filed pro se were all denied (0/16), against 7/52 grants among
  counseled ones. That matches the Court's general practice: a pro se stay application
  is denied on the papers essentially without exception.
- **Respondent is a court (strong, downward).** All 6 substantive applications in the
  same pull whose respondent was a court (three of them naming a federal district
  court or superior court directly) were denied. Mandamus-posture applications have
  no realistic prospect of four votes for certiorari or an extraordinary writ.
- **No counsel, no amici, no response requested (moderate, downward).** The
  application sits at the bottom of every ladder rung; the pool's 20% is drawn
  largely from counseled, often government or capital, applications.

Net: P(unqualified grant) = **0.01**. I do not go lower because the resolver scores
the disposing entry's text and a stray parse of an administrative or partial order
could read as a grant, and because a 1% floor is where I am honestly indifferent.

## The three increment claims

- `response-requested-increment` 0.04: a Circuit Justice calls for a response when
  the application has some prospect; pro se mandamus-posture applications almost never
  draw one. The statpack's 24 of 70 (Term 2024) response-requested count is over all
  substantive applications, pending included, and is dominated by counseled filings.
- `referral-increment` 0.35: the statpack shows referral is common in the pooled
  slice (54 of 70 substantive applications in Term 2024, 107 of 227 in Term 2025),
  but that count is selection-loaded. For a pro se application the realistic paths are
  Justice Kagan referring on receipt, or a chambers denial followed by a renewed
  application to another Justice, which is referred under the same number. I weight
  the single-Justice denial as the modal outcome.
- `amicus-increment` 0.01: no plausible amicus interest.

## Uncertainties and where to discount me

- I could not locate Ninth Circuit No. 25-2374 in CourtListener's RECAP index, so the
  mandamus reading rests on the caption and on the number's neighbourhood among
  spring-2025 Ninth Circuit petitions against district courts, not on the petition
  itself. If the underlying matter were instead a sensitive criminal or immigration
  matter with counsel entering later, the response and referral numbers would move
  up; the grant number would barely move.
- No filed-document text was provisioned, so I have not read the application.
- The application was submitted on Nov 18 2025 and this forward cell runs on
  Sep 30 2026 with the event marked unresolved. A stay application is almost always
  disposed of within weeks, so the docket has very likely resolved and the corpus has
  simply not parsed the disposition. I did not retrieve this docket's later state or
  its outcome; see `flags.json`.
- `big_case_score` 0.02: single pro se litigant, no public stake.
