# Rationale — P(unqualified grant) = 0.01

**The cell.** Interim stage, `moment: arrival`, `forward` mode, application
Term 2026. The provisioned snapshot (`record/snapshots/2026-09-28.json`,
provenance `truncated`, cutoff 2026-09-28, `arrival-position` cut anchored at
entry 0) shows exactly one docket entry: "Application (26A449) for a stay,
submitted to Justice Alito" (Sep 27, 2026), docketed October 2, 2026, lower
court Supreme Court of Texas (26-0569). The caption is *Elisha Holloway,
Applicant v. Bryan Polk*; counsel of record is the applicant herself, so this
is a pro se filing. The frozen context carries the ladder at its floor —
`response_requested: false`, `referred_to_court: false`, `amicus_briefs: 0` —
and `band: null`, the normal interim state, so I did not derive a band or read
the cert band table.

**What I could not read.** `documents.json` lists the application (44 pages,
fetched 2026-10-03) with `empty_text: true`, and `application.txt` is blank.
The filing's text was unavailable, so the ask is read from the docket entry's
own words and I do not know what Texas judgment the stay targets. This is
recorded in `flags.json`.

**Published baseline.** `metrics/statpack.md` carries "The interim docket
(applications)" with the scored-base-rate caption. For an application-Term
2026 cell the pool is Terms strictly before 2026 and within ten Terms: OT2025
contributes 226 resolved substantive applications (17 granted) and OT2024
contributes 70 (14 granted); OT2016–OT2023 are entirely unparsed and add
nothing. Pooled: 31 / 296 ≈ **10.5%**, which clears the pre-registered floor
of 50 resolved. That is the yardstick this cell is scored against. The two
Terms differ (7.5% against 20.0%), and the OT2024 row sits on 972 unparsed
applications, so the spread is coverage as much as behaviour.

**Adjustment down, and why it is large.** The pooled rate is measured over a
cohort dominated by counseled applications, many governmental, many referred
and briefed (the section counts 178 referrals and 64 response requests across
367 substantive applications). This application is at the opposite end of
every observable:

- **Pro se applicant, individual respondent, state civil matter.** A RECAP
  party-name search placed the applicant as a repeat self-represented litigant
  in Texas landlord-tenant and consumer matters (several N.D. Tex. suits in
  2023–2025, a Fifth Circuit appeal, a Fort Worth mandamus in 2024, and Waco
  court of appeals decisions in 2025 and April 2026), plus a pending pro se
  civil-rights suit captioned *Holloway v. Polk* in N.D. Tex. (4:25-cv-01128,
  filed October 2025). I did not get to read any of those dockets or opinions
  before the CourtListener throttle hit, so I take from them only the class of
  litigant and the general subject matter, not any fact about the Texas
  judgment at issue.
- **A stay of a state-court judgment is a hard ask.** It needs a reasonable
  probability of a cert grant plus a fair prospect of reversal on a federal
  question, and nothing about a landlord-tenant or civil-rights dispute of this
  shape suggests one the Court would take.
- **No escalation signal has fired**, which is consistent with an application
  headed for a prompt single-Justice denial.
- **The current Term's comparable stream points the same way.** The two
  resolved substantive applications `fedcourts query` returned for late
  September and early October 2026 (26A370, 26A447) were both denied; the
  Term-2026 row shows 6 grants in 63 resolved, and the grants in this
  population go to institutional applicants with contested equities.

I put the disposition at **0.01**, an order of magnitude under the pooled
baseline and about as low as I price any application given order-entry noise
(a clerical surprise or a mixed order the resolver reads unexpectedly).
`withdrawn` and `dismissed` both count as ungranted, which only reinforces the
low number.

**Ladder claims.** `response-requested-increment` 0.03: a response call is an
act of attention this filing is unlikely to draw. `referral-increment` 0.10:
higher than the other rungs because a renewed application after a
single-Justice denial is sometimes docketed as a referral on the same number,
and some Justices refer weak applications so the denial issues from the full
Court; still well below the cohort's raw referral share, which is driven by
counseled applications. `amicus-increment` 0.01: no organized interest exists
here.

**Stakes.** `big_case_score` 0.02: no doctrinal question is visible, no
institutional party is involved, and the outcome matters to the parties only.

**Uncertainty and discounts.** My read of the ask rests on one docket line
because the application text was unextractable. The underlying Texas
proceeding is unread, and the N.D. Tex. *Holloway v. Polk* docket, which would
have said who the respondent is and what the dispute concerns, was located but
not fetched after CourtListener returned HTTP 429 (shared 300/hour limit)
on the first endpoint call; I did not wait for the reset. Those gaps bound how
confident I can be about *why* the application fails, not whether it does:
nothing I could have read would plausibly raise a pro se stay application from
a state civil matter above a few percent. No call sought this application's
disposition and none surfaced it.
