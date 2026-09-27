# Why 0.35, and where to discount me

## Mode, inputs, and anchor

Forward cell (`record/context.json`: mode `forward`, cutoff 2026-09-26 under a
`date` cut, `band: null`, `response_requested: true`, `referred_to_court:
false`, `amicus_briefs: 0`, term 2026). I read the provisioned snapshot
`2026-09-25.json` (three entries: application submitted to Justice Kagan
September 16; response requested September 18; response filed September 25),
the provisioned `record/documents/application.txt` (the 189-page stay
application including appendix, `truncated: true`, text present), and
`documents.json`. No band applies at the interim stage and I did not derive one.

**Anchor.** The committed `metrics/statpack.md` section "The interim docket
(applications)" carries the scored base rate. Pooling the per-Term
`substantive_granted` / `substantive_resolved` counts for application-Terms
strictly before 2026 within the ten-Term window: Term 2025 gives 17 of 226 and
Term 2024 gives 14 of 70; Terms 2023 and earlier show zero resolved (fully
`unparsed`). Pool: 31 granted of 296 resolved, about 10.5 percent, which clears
the 50-resolved floor. The section's caption already describes the rate as
grounding the scored baseline, so I read the scored version. The Term 2024 row
sits on 972 unparsed applications, so the 20 percent figure there is on partial
coverage and the pool leans on 2025. That pool is dominated by pro se, capital,
and private applicants (the `fedcourts query` denied list confirms the shape),
so it is a floor for this applicant class, not a description of it.

## Adjustments up from the anchor

- **Applicant class and counsel.** A State acting through its Attorney General
  with Paul Clement as counsel of record. State applicants asking this Court to
  stay lower-court orders that displace state administration fare far better
  than the docket-wide rate; in the current Court's practice such applications
  have been granted roughly as often as denied when the Court gives them full
  consideration.
- **Response called for.** The one escalation rung that has fired is the
  affirmative-attention one. It is routine for a state application, so the
  information is modest, but it removes the summary-denial tail.
- **Doctrinal tilt.** The six-Justice majority has been receptive to
  state-sovereignty framings of irreparable harm and skeptical of expansive
  equitable remedies (CASA). In Barnes v. Ahlman (2020) the Court stayed a
  PLRA jail-conditions injunction 5-4 for a government applicant; the Court is
  more conservative now than then. A private receiver taking over a state
  agency for five years is an unusually vivid version of that concern.
- **Split below.** Judge Forrest dissented in part from the Ninth Circuit's
  September 1 denial, and the panel majority (Judges S.R. Thomas and Berzon)
  is one the Court's majority frequently reverses.

## Adjustments down

- **Certworthiness.** The opposition's strongest point, and the one that
  matters most to Justices Kavanaugh and Barrett, who have both said the
  emergency docket tracks certworthiness. The application's cert argument is
  two sentences. The core claim (no post-injunction contempt cycle, wrong time
  window, five years for the receiver versus three for the State) is an
  abuse-of-discretion challenge to a fact-bound remedial judgment after a
  fifteen-day trial, two contempt findings and about 2.6 million dollars in
  fines. There is no circuit split.
- **The CASA hook is weak here.** Respondents say it was never raised in the
  district court, and the applicants themselves say the Court need not reach
  it. That leaves the "big question" without a vehicle.
- **Vehicle and timing.** The Ninth Circuit expedited the appeal (opening brief
  filed September 15, answering brief due October 15, argument in December) and
  its motions panel expressly left the stay open to the merits panel. The
  Atiyeh v. Capps line, quoted by respondents, counsels against Circuit Justice
  or Court intervention while an appeal is actively pending.
- **Equities cut against the State's framing.** The 2023 injunction was
  stipulated and never appealed, the receiver was a person the Department
  itself nominated, the district court already delayed the effective date to
  October 19, and the record includes deaths the court-appointed experts found
  preventable. Respondents' opposition (48 pages, ACLU and Prison Law Office)
  presses these hard and reads as a competent, well-cited brief.
- **Partial-grant collapse.** A stay limited to the state-law-waiver provisions
  or otherwise qualified would resolve as ungranted under the pre-registered
  rule, and that shape is a real fraction of the grant-side mass.

Net: I moved from about 0.10 to 0.35. The main uncertainty is how the Chief
Justice, Justice Kavanaugh and Justice Barrett weigh sovereignty against the
fact-bound and interlocutory posture. I would not be surprised by a 6-3 grant;
I would be more surprised by a unanimous denial without any noted dissent.

## Claim-by-claim

- `interim-disposition` 0.35: equals the top-level probability.
- `response-requested-increment` 0.03: the rung has fired, so the harness masks
  it; the number is the chance of a supplemental response request.
- `referral-increment` 0.90: not yet on the record. For an application of this
  profile the Circuit Justice almost always refers to the Court; the residual
  is Justice Kagan acting alone or the docket failing to record the referral
  as a separate entry.
- `amicus-increment` 0.35: zero entries after nine days including the response
  day is a negative signal, but Arizona's legislative leaders filed as amici
  below and a state coalition is plausible on this framing.

## Retrieval beyond the provisioned inputs, and its bearing

- Two `fedcourts query` calls (granted and denied substantive applications,
  `--include-applications`) for the shape of the pool. The granted list was
  mostly time-extension applications and two high-profile substantive ones;
  the denied list was pro se and capital applications. Used for shape only.
- CourtListener MCP: the Ninth Circuit dockets 26-5060 and 26-1746, to read
  the September 1 stay order (panel composition, the "subject to
  reconsideration by the merits panel" language, the expedited schedule, and
  the legislative-leaders amicus below). An opinion search for the case
  returned nothing.
- The respondents' opposition, fetched from the Supreme Court's public docket
  PDF named in the snapshot's own entry of September 25 and text-extracted
  locally. It was filed before my cutoff and is the entry that opened this
  event, but it was not provisioned (flagged in `flags.json`). It moved me
  down by several points, mainly on certworthiness, forfeiture of the CASA
  argument, and the stipulated-injunction and nominated-receiver facts.

Nothing I retrieved postdates the snapshot or touches this application's
disposition. I did not read anything under `data/qp-topics/`.

## Where to discount me

I have no calibrated reference class for "state applicant, response requested,
structural-remedy stay" from the corpus; the class-level rates above are my
own read of recent practice, not a committed cut. The statpack's pool rests on
two Terms with uneven parse coverage. And the interim baseline is unconditioned
on the escalation ladder while this cell was selected on it, so any skill
number against it is weak evidence either way.
