# Why 0.63

**Inputs read.** The provisioned snapshot `record/snapshots/2026-10-08.json`
(five docket entries, through the two October 8 amicus submissions),
`record/context.json` (forward mode, `date` cut at 2026-10-09, band null,
`response_requested: true`, `referred_to_court: false`, `amicus_briefs: 2`,
Term 2026), the provisioned `application.txt` (the Solicitor General's 40-page
application, fully extracted), and `event.yaml` (stage interim, moment
response-filed, opened 2026-10-08). The respondents' opposition was filed
before the snapshot date but was not provisioned; because this is a forward
cell I fetched the PDF from the Court's docket and extracted its text, and I
read the D.C. Circuit's September 18 per curiam order and Judge Walker's
dissent in full through CourtListener. I also confirmed on the Court's own
docket page and SCOTUSblog that nothing has been entered after October 8 and
no disposition exists.

**Baseline.** The committed statpack's "The interim docket (applications)"
section carries the scored base rate. Pooling the substantive resolved rows
over application-Terms strictly before 2026 and within ten Terms (2016 to
2025) gives, from the table itself, Term 2025: 226 resolved and 17 granted;
Term 2024: 75 resolved and 14 granted; every earlier Term is entirely
unparsed. Pool: 31 of 301, a grant rate of 10.3%, which clears the
pre-registered floor of 50. The section's caption already calls this the
scored rate (not the older descriptive-only wording). Two cautions I read from
the table: the pool rests on only two parsed Terms, and Term 2024 was reached
only in part (937 unparsed rows), so the pooled figure is a coverage artifact
as much as a behavioural one. The cert band table is not an anchor for an
interim cell, and the context's band is null in any case.

**Why I moved far above the baseline.** The pooled population is every
substantive application: capital-case stay requests, pro se habeas applicants,
private litigants seeking injunctions pending certiorari. This applicant is
the Solicitor General, and the public trackers I consulted put the
administration's emergency-docket record since January 2025 at 24 of 32
rulings at least partly in its favour (Brennan Center, updated September 29,
2026) and 21 of 27 favourable through January 2026 (Bloomberg Law). Discounting
for partial grants, which the resolver reads as ungranted, the government's
unqualified-grant rate on contested applications sits somewhere near 0.6 to
0.7. The two closest topical priors, Shilling (military service) and Orr
(passports), were both stays of transgender-policy injunctions granted six to
three on the merits, and both involved APA arbitrary-and-capricious holdings
below. The application's strongest cards are the shape of the order (a
universal Section 705 stay plus a nationwide class injunction), Wolfish and
Turner deference, Skrmetti's "medical uncertainty" framing, and the recent per
curiams finding certworthiness and irreparable harm satisfied whenever a
federal program is set aside. The D.C. Circuit majority (Wilkins and Garcia,
with Walker dissenting) is a panel this Court's majority has reversed on
emergency matters before.

**Why not higher.** Four things in the opposition and the orders below are
real. First, the record gap is specific and both courts below found it: the
administrative record says nothing about BOP's own three decades of providing
the care, on either the medical or the security rationale, and the Stahl
declaration is post hoc. That is a conventional State Farm problem, not a
policy disagreement, and a Justice inclined to limit the emergency docket to
clear cases can rest on it. Second, delay: the government never appealed the
June 2025 injunction, took seven weeks to seek a stay of the June 17, 2026
order in the D.C. Circuit, and claimed no irreparable harm in the district
court. Third, the harm asymmetry is more concrete than in Orr: tapering
hormone therapy from a certified class of about a thousand prisoners, with
declarations of self-harm during the 2025 cutoff, against an abstract
intrusion injury. Fourth, the three-component policy (surgery, hormones,
accommodations) invites a split order, and any "granted in part" resolves as
ungranted. I also give a few points to dismissal or withdrawal because the
August 26 order is a rolling 90-day PLRA injunction that lapses around
November 24; the D.C. Circuit already dismissed the stay motion against the
June 17 order as moot when that one expired.

**Net.** Full grant 0.63, full denial about 0.25, partial grant about 0.08,
dismissed or withdrawn about 0.04. The scored number is P(unqualified grant)
= 0.63, which is the top-level `probability` and the `interim-disposition`
claim. Where a reader should discount me: the government-applicant win rate I
leaned on is from public trackers with a small denominator and a mixed
partial/full coding, not from the corpus; and I have no conditioned corpus cut
for a federal applicant or for the response-requested rung.

**Ladder claims.** `response-requested-increment` is 1.0 because the rung has
already fired on the record (September 28); the harness will resolve it as
vacuous. `referral-increment` is 0.92: the disposing entry on an SG
application after a requested response carries the "referred to the Court"
recital almost without exception, and the harness's referral regex reads that
entry; the complement is essentially the dismissal/withdrawal branch plus
wording variance. `amicus-increment` is 0.5: the count stands at 2, both
supporting the applicants and both filed on the response day; respondent-side
amici have appeared on every comparable application but the window has
largely closed and the matter should resolve within weeks.

**Votes.** Six to three on the Orr and Shilling lineup, with Jackson writing a
dissent joined by Sotomayor and Kagan. These are banked, not scored, and the
most uncertain names are Roberts and Barrett, either of whom could author or
join a narrowing partial grant.

**Big-case score.** 0.6: a nationwide class, Executive Order 14168, and the
third transgender-policy emergency application in two Terms, but a narrower
legal question (APA review of a prison medical policy) than the headline cases
of the Term.

**Corpus tooling.** Two `fedcourts query` calls with `--include-applications`
returned rows dominated by same-day time-extension grants and cert denials;
they confirmed the corpus's labelling conventions but contributed no usable
prior. The corpus-wide vintage was not checked with `corpus-info` because the
cell has no local blob; the corpus service answered the queries live.
