# Reasoning: why 0.72 for an unqualified grant

## What I read

- `record/context.json`: mode `forward`, stage interim, moment
  `response-requested`, `band: null` (normal for an application; I did not
  derive one), `response_requested: true`, `referred_to_court: false`,
  `amicus_briefs: 0`, cutoff 2026-09-29 under a `date` cut, term 2026.
- `record/snapshots/2026-09-28.json`: two docket entries, both September 28,
  2026. The application was submitted to the Chief Justice, and the Chief
  Justice requested a response due October 8, 2026. No administrative stay
  was requested or entered. Lower court: D.C. Circuit Nos. 26-5236 and
  26-5310.
- `record/documents/application.txt` (40 pages, full text, not truncated):
  the Solicitor General's application. I read it in full. It seeks a stay of
  the August 26, 2026 order of the D.D.C. (a renewed 90-day PLRA preliminary
  injunction and § 705 stay) blocking BOP's February 2026 gender-dysphoria
  policy as to every inmate diagnosed with gender dysphoria. The D.C. Circuit
  denied a stay 2-1 on September 18, 2026 (Judge Walker dissenting), resting
  only on BOP's alleged failure to consider its own prior experience. The
  government argues APA deference, prison-administration deference, harmless
  error given two independent justifications, and two PLRA defects
  (no particularized findings; relief broader than the harm found, including
  surgery and a universal class).

## Anchor

The statpack's interim section carries a scored base rate. For an
application-Term 2026 cell the strictly-prior pool is Terms 2024 and 2025
(Terms 2016-2023 are fully unparsed and contribute nothing):

| Term | resolved (subst.) | granted | unparsed |
| --- | --: | --: | --: |
| 2025 | 226 | 17 | 0 |
| 2024 | 70 | 14 | 972 |
| pooled | 296 | 31 | — |

Pooled rate 31/296 = **10.5%**, which clears the 50-resolved floor, so this is
the baseline my skill is scored against. Term 2024 is only partly parsed (972
of 1297 applications unparsed), so the pool leans on Term 2025. The section's
caption already describes the rate as the scored base rate, not as
descriptive-only.

That pooled rate is a floor for this cell, not an estimate of it: it pools
every substantive application, including the many pro se and capital
applications that are denied without a response ever being requested. The
statpack's escalation columns are not as-at-prediction and are right-censored,
so I used them for shape only.

## Adjustments from the anchor

**Up, strongly, for the escalation ladder and the applicant.** The Chief
Justice requested a response the day the application arrived. In the corpus's
recent window (a 400-row `fedcourts query` pull yielding 69 resolved
substantive applications from roughly August to September 2026), the rate
among applications where a response was requested was 6/11 granted versus
1/58 where none was, and 6/7 where a response was requested and the matter
was referred. Applications with the Solicitor General as applicant went 4
granted, 1 denied (USPS v. California, 26A305), 1 withdrawn. These are small
samples from one Term and I have not treated them as a base rate, but they
point the same direction as the Court's public record since 2025: the
government has won the large majority of its emergency applications, and the
two closest analogues on gender-identity policy both ended in full stays over
three dissents (the transgender military-service stay in Trump v. Shilling,
May 2025, and the passport sex-marker stay in Trump v. Orr, November 2025,
which this application cites). United States v. Skrmetti (2025) and West
Virginia v. B.P.J. (2026), both cited in the application, show a majority
that treats gender-dysphoria treatment as an area of "medical and scientific
uncertainty" where policymakers get deference.

**Up for the legal posture.** The order under review is a class-wide,
universal § 705 stay against a nationwide federal policy, the shape the Court
has repeatedly stayed since Trump v. CASA (2025), and the application's APA
argument (a 3200-page record, a 43-page explanation, two independent
justifications, and a court of appeals that adopted only one narrow ground)
maps onto Wages & White Lion and Prometheus Radio. The PLRA arguments give
the Court a narrower off-ramp if it wants one. Judge Walker's dissent below
gives the majority a ready-made rationale.

**Down for the harm story and the partial-grant risk.** The injunction
protects inmates currently receiving hormone therapy from a tapering plan,
and the district court found irreparable harm on that basis. That is a more
concrete harm than the passport or military cases presented, and it is the
provision most likely to draw a carve-out. The interim resolver reads a
"granted in part" as ungranted, so I have to price a partial stay (surgery and
social accommodations stayed, hormone tapering not) as a miss. I put that at
about 0.10. The D.C. Circuit did not expedite the appeal (appellant's brief
November 2, reply December 23), and the 90-day PLRA injunction expires around
November 24, 2026, so a Justice could argue the Court should let the ordinary
process run. I weight that lightly because the district court has renewed the
injunction every 90 days since June 2025 and the government's harm argument
is about the standing policy, not this one order.

**Net.** From a 10.5% scored floor I move to 0.72 for an unqualified grant,
leaving roughly 0.16 for denial, 0.10 for a partial grant, and 0.02 for
withdrawal or dismissal.

## The three increment claims

- `response-requested-increment` = 1.0. The rung has already fired (the
  September 28 request is in my snapshot), so the harness will mask this claim
  as vacuous for my cell. I state it at 1.0 to say plainly that the record I
  was shown already carries the request.
- `referral-increment` = 0.93. Referral is near-certain for a Solicitor
  General application with a requested response; the residual is a
  withdrawal before referral.
- `amicus-increment` = 0.88 from a count of zero. Every federal-government
  application with a requested response in the recent corpus window carried
  amici (2, 7, 10 and 13 entries on the four granted ones). The residual is a
  fast disposition before amici file, or a withdrawal.

## Votes and stakes

The vote block is optional on an interim cell and unscored; I include a 6-3
lineup as context only. `big_case_score` 0.7: a nationwide class of federal
inmates, forced tapering of hormone therapy, and the first Supreme Court
encounter with BOP's post-Skrmetti policy make this a closely watched
application, but it is an interim order and the merits are months away.

## Where to discount me

- The corpus cross-tabs are one Term's worth of rows and were filtered by me
  from a recency-ranked pull, not a designed sample. The statpack's 10.5% is
  the only committed baseline.
- I did not read the respondents' opposition (none exists yet) or the D.C.
  Circuit's order text beyond the docket description; my reading of the
  panel's reasoning is the government's characterization of it.
- I know the Court's 2025 stay orders in Shilling and Orr from general legal
  context, not from a provisioned document. They predate the snapshot and are
  legitimate forward signal, but my recollection of their votes is from
  memory.
- Retrieval was healthy: the corpus service answered four queries and the
  CourtListener MCP server answered four calls. Nothing surfaced about this
  application's own disposition, which cannot exist before the October 8
  response date.
