# Why these numbers

**P(unqualified grant) = 0.80.**

*Anchor.* The committed `metrics/statpack.md` carries an interim-docket
section with a scored base rate. This application is 26A406, so its
application Term is 2026 and the pool is Terms 2016 through 2025. Only two
of those Terms carry resolved substantive rows: Term 2025 (226 resolved, 17
granted) and Term 2024 (70 resolved, 14 granted). Pooled, that is 31 of 296,
a grant rate of about 10.5%, which clears the pre-registered floor of 50, so
this is the published baseline the cell is scored against. The section's
caption already describes the rate as the scored baseline rather than
descriptive-only. Two cautions travel with it: Term 2024's `unparsed` column
is 972 against 70 substantive rows, so the pool rests partly on a Term the
poller reached only in part, and the pooled cohort is unconditioned on the
escalation ladder while this cell was selected on it.

*Why I sit far above the anchor.* The pooled 10.5% describes every
substantive application, most of them pro se or private stays denied without
a response ever being requested. This application is different on every
dimension the record lets me see:

- The applicant is the Solicitor General. Federal-government emergency
  applications in the last two Terms have succeeded at a rate far above the
  docket's, and the corpus rows I pulled (`fedcourts query`) show the recent
  SG-filed substantive applications resolving as grants (26A308, DHS v. League
  of Women Voters, with a requested response, referral, and ten amici).
- The Court has twice granted the government relief in this very case: the
  June 23, 2025 stay of the preliminary injunction (145 S. Ct. 2153) and the
  July 3, 2025 clarification (145 S. Ct. 2627). The application (which I read
  in full from `record/documents/application.txt`, 45 pages, not truncated)
  shows the final judgment rests largely on the same grounds the stayed
  injunction did, with two additions: that Section 1252(f)(1) does not reach
  declaratory judgments and vacatur, and that Section 1231(b) itself implies
  notice-and-opportunity procedures. The first was expressly reserved in
  Biden v. Texas, so it is open, but the Court's own stay in 2025 already
  treated the classwide relief as likely barred, and the second runs into
  Section 1231(h)'s text, which the First Circuit answered by reading the
  statute "to mean more than what it plainly says." The Court's recent
  interim orders (Boyle, National TPS Alliance) instruct lower courts to
  follow its interim rulings in like cases, and this is the same case.
- The escalation ladder is at its strongest rung: a response was requested
  the day of filing. That is a signal of attention, not of outcome, but it
  removes the largest denial mode (summary denial without a response).
- The equities the Court credited in 2025 (foreign-policy disruption,
  removal of criminal aliens whose home countries refuse them) are restated
  with fifteen months of operation under the policy behind them, and the
  First Circuit's dissolution of its stay at 11:36 p.m. without a response
  (confirmed on the CA1 docket via CourtListener) gives the Court a
  procedural irregularity to point to.

*Why not higher.* Three things hold the number at 0.80 rather than 0.90.
First, the resolver's denial-first collapse: any "granted in part" order
scores as ungranted. The judgment has separable pieces (declarations,
vacatur, the class definition including admitted and unadmitted aliens), and
the Court has in the past stayed relief only to the extent it exceeded the
named plaintiffs' complete relief (CASA); Section 1252(f)(1) itself preserves
individual relief, so a stay that carves out the four named respondents is a
live shape. I put roughly 0.08 to 0.10 on a mixed order. Second, the posture
has changed: this is a final judgment affirmed on a full merits record, not a
preliminary injunction, and the First Circuit's statutory ground is new, so
one or two Justices in the 2025 majority could view the merits question as
one the Court should decide with briefing rather than by stay. Third, a
residual chance the Court defers the application pending expedited
certiorari or otherwise disposes of it in a form the resolver does not read
as a grant. The votes I recorded (6 to 3, Sotomayor dissenting with Kagan and
Jackson) are a forecast of the 2025 lineup repeating; they are optional on an
interim cell and unscored.

**response-requested-increment = 0.99.** The record already shows the
request (September 24, due September 28). The claim is vacuous for this cell
and the harness masks it; I state a probability because the contract asks
for one on every declared claim.

**referral-increment = 0.95.** Frozen context shows `referred_to_court:
false`. A single-Justice disposition of a contested SG application with a
requested response is nearly unheard of, and the government asked that even
the administrative-stay request be referred. The residual is resolution
noise: the resolver reads referral from docket text ("by her referred to the
Court"), and a docket that resolves the matter in an unusual phrasing, or a
withdrawal or mooting before disposition (for example the First Circuit
reinstating its stay), would leave the increment unresolved or false.

**amicus-increment = 0.60.** Frozen context shows zero amicus entries. The
statpack shows amici on about 18% of substantive applications overall (65 of
367), but high-profile SG immigration applications draw amici at a much
higher rate (26A308 drew ten; the 2025 round in this case drew filings).
Against that, the response window is four days and the Court may act within
days of the reply, and the resolver counts entries reciting amicus/amici
curiae or "Amicus brief of X submitted", so a brief that never reaches the
docket before disposition does not count. I lean slightly above even.

**big_case_score = 0.78.** Nationwide third-country-removal policy, a
classwide judgment with universal vacatur, an open Section 1252(f)(1)
question on declaratory relief and vacatur, cabinet-level declarations on
foreign policy, and a third emergency round in one case. Not at the very top
because the stay order itself will likely be unexplained and the doctrinal
payoff waits for a merits case.

**What I did not have and where to discount me.** No response or reply is on
the record (the response is not due until September 28), so the respondents'
side is inferred from the lower-court opinions as the application describes
them. I did not retrieve the First Circuit's September 18 opinion text; the
application's summary of it is the government's framing. The CourtListener
search for the SCOTUS application docket returned nothing, so I could not
check whether an administrative stay, referral, or amicus filing landed after
the snapshot; the cell is forward and I found no indication the application
has been decided. I carry the outcome of the 2025 rounds from the application
itself and from general knowledge; both predate this event and are legitimate
forward signal. The `fedcourts query` priors surface by recency, so I could
not pull the 2025 D.V.D. application row (24A1153) to check its recorded
amicus count. The corpus rows were read from the cell's corpus service; I did
not run `corpus-info`, so I cannot state the blob's vintage beyond the fact
that it carried Term 2026 applications numbered through 26A408.
