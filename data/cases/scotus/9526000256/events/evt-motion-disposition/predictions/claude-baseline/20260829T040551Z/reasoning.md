# Rationale — why P(grant) = 0.01

**The cell.** Interim stage, `moment: arrival`, forward mode. Application
26A256 (Term 2026), Cassandra Perkins v. United States District Court for the
Northern District of Georgia, et al., submitted to Justice Thomas (Circuit
Justice for the Eleventh Circuit) on August 11, 2026 and docketed August 25.
The frozen context shows the escalation ladder at zero: no response requested,
not referred to the full Court, no amicus briefs. `band` is null, as an
interim cell's should be, so no cert band table was consulted.

**The published baseline.** The committed statpack carries "The interim docket
(applications)" with the scored-base-rate caption (not the older
descriptive-only one). Pooling the resolved substantive slice over
application-Terms strictly before 2026: Term 2025 contributes 178 resolved /
16 granted and Term 2024 contributes 49 / 14, for a pool of 227 resolved and
30 grants — clearing the pre-registered 50-resolved floor — giving a pooled
baseline of **13.2%**. That is the yardstick this cell is scored against, and
it is where I anchored.

**Why I moved far below it.** The pooled cohort is dominated by represented
parties — chiefly the federal government and institutional litigants — whose
emergency applications the recent shadow docket grants at high rates; that is
what puts the pooled rate at 13%. This application shares none of those
features:

- The applicant is self-represented (she is listed as her own attorney, with
  no counsel of record) and the application is linked to an IFP-range cert
  docket (26-5339).
- The respondent is the district court itself. Asking one Justice to enjoin
  the court presiding over the applicant's own civil suits is relief the
  Court essentially never grants; the proper vehicle for such complaints is
  mandamus or appeal, and the All Writs Act standard for an original
  injunction from a Circuit Justice is far beyond this record.
- The underlying litigation, so far as RECAP shows, is two pro se ADA
  employment suits in the N.D. of Georgia (Perkins v. United Health Group
  Optum, 1:24-cv-01551; Perkins v. Ascension Health, 1:24-cv-05425, both
  before Judge Leigh Martin May), each opened with an IFP application. The
  Eleventh Circuit case the snapshot names (25-12952) is not in RECAP, so I
  could not read the order being complained of; nothing about the visible
  posture suggests a plausible entitlement to emergency relief.
- No rung of the escalation ladder has fired, and I expect none to.

Pro se applications of this shape are denied at a rate close to 100%. I set
P(unqualified grant) at **0.01** — effectively the floor, holding back only
for the irreducible chance that the docket entry resolves oddly rather than
that relief is actually granted.

**The increment claims.** Response-requested 0.02 and amicus 0.02: both
require someone other than the applicant to treat the application as live,
which no visible feature invites. Referral 0.10: denial by the Circuit
Justice alone is the modal path, but referral-then-denial is a real minority
pattern (the statpack's referred count, 95 of 263 substantive applications, is
right-censored and cohort-skewed toward big cases, so I read it as shape only
and discounted it heavily for a pro se applicant).

**Uncertainty and discounts.** My largest gap is the content of the
application itself — the snapshot links the PDF but I did not retrieve it, and
RECAP's coverage of the underlying dockets is two entries each — so I cannot
rule out an unusual underlying dispute. That uncertainty moves the referral
and timing forecasts more than the disposition: even an unusual pro se
application against a district court is denied. The statpack's Term-2024
parse coverage is partial (977 unparsed applications), so the pooled 13.2%
baseline blends uneven coverage; that caveat travels with the number but does
not change my direction of adjustment. The `fedcourts query` sweep returned
mostly time-extension applications whose routine grants say nothing about a
substantive injunction ask; I did not lean on it.
