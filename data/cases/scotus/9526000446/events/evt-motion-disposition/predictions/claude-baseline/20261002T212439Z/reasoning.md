# Reasoning for the numbers

**Cell.** Interim stage, `moment: arrival`, forward mode. Snapshot `2026-09-30.json`,
cut `arrival-position` at the single entry "Application (26A446) for a stay, submitted
to Justice Kavanaugh" (Sep 29 2026). Context: `band: null` (as expected on an
interim cell; I did not derive one), `response_requested: false`,
`referred_to_court: false`, `amicus_briefs: 0`, `term: 2026`. One provisioned
document, `application.txt` (44 pages, not truncated, text extracted), which I read
in full.

**Anchor.** The committed statpack's "The interim docket (applications)" section. For
application-Term 2026 the strictly-prior ten-Term window is Terms 2016–2025; only
2024 and 2025 carry parsed substantive rows (the earlier Terms are wholly unparsed),
so the pool is 2025 (226 resolved, 17 granted) plus 2024 (70 resolved, 14 granted):
296 resolved, 31 granted, a pooled rate of about 10.5%, which clears the
pre-registered floor of 50. That is the yardstick this cell is scored against. The
section's own caption already describes the rate as the stage's scored base rate, so I
read the current caption rather than the older descriptive-only one. Caveats that
travel with it: 2024 is heavily unparsed (972 of 1,297 applications), and the pooled
cohort is not conditioned on the escalation ladder while predicted cells are selected
on it.

**Where 0.12 comes from.** Three pulls in opposite directions, from the pooled 10.5%.

- *Up:* Justice Kavanaugh called for a response on October 2 (observed on the
  supremecourt.gov page for the linked petition, No. 26-391, as a post-baseline
  forward signal; see `flags.json`). In the 500 most recent application rows the
  corpus served, 86 were substantive and resolved; grant rate 33% (6/18) with a
  response requested against 3% (2/68) without. The application is counseled by
  experienced Supreme Court practitioners, rests on a 5-4-3 split that the Sixth
  Circuit's own stay-denial order acknowledged, and has a dissent below applying the
  deferential standard and reaching the opposite result, so the cert-probability
  prong is genuinely strong.
- *Down, and harder:* the response-requested lift in that sample is almost entirely
  federal-government applicants (the United States as applicant granted 4 of 9; private
  applicants against a federal respondent granted 1 of 10). A private criminal
  defendant asking the Court to undo a court of appeals' detention order over the
  government's dangerousness case is a class the Court essentially never grants; a stay
  here means release, not preservation of the status quo. The government's response
  will lean on the panel's findings that Wagner solicited funds to evade law enforcement
  and that conditions would not mitigate the risk, and the equities in a
  threats-and-cyberstalking prosecution are contested. The Court can also reach the
  split through the petition itself (a motion to expedite is pending, and the United
  States has waived its response to the petition, which would put it before the
  Conference quickly), so denying the stay costs the Court nothing on the legal
  question.
- *Mootness pressure cuts both ways:* trial is set for November 3 with a stipulated
  60-day extension available; that argues for the Court acting quickly on the
  petition, not for a stay.

I land at 0.12: a little above the pooled anchor because an affirmative act of
attention has already happened and the legal question is serious, well below the
33% conditional figure because the applicant class drives that figure.

**Increments.**
- `response-requested-increment` 0.96: already fired after the frozen state; residual
  for the chance that the harness's read of the application docket differs from the
  petition-docket mirror I saw.
- `referral-increment` 0.72: among the 18 response-requested substantive applications
  in the sample, 12 were referred; the six that were not were mostly quick
  single-Justice denials. A called-for response on a split of this kind usually goes
  to the Conference.
- `amicus-increment` 0.50: 16 of 18 response-requested applications in the sample drew
  amici, but those were overwhelmingly high-profile government or election matters; a
  private detention application draws fewer, and a brief filed on the petition docket
  would not count here. Six days to the response and a week or two to disposition
  leave room for one or two filings.

**Big case.** 0.55 on the stakes axis: the split is old, acknowledged, and affects a
very large volume of bail decisions, and the defendant's detention on the strength of
anti-ICE speech makes the matter newsworthy; the application itself disposes only of a
stay, which tempers the score.

**What I did not use.** No outcome of this application surfaced anywhere I looked.
The Washington Times coverage of October 2 was unreachable (HTTP 403) and the
CourtListener docket search returned nothing for this matter, so the live-state
reading rests on the Court's own docket pages. I did not read anything under
`data/qp-topics/`.

**Where to discount me.** The 86-row corpus sample is recent-Term only and small once
sliced by applicant class, so the class-conditional rates are indicative, not
estimates. I have no committed cut conditioning the interim base rate on the
escalation ladder, which is exactly the signal this cell turns on. The 26A446 docket
page itself had not yet shown the October 2 entry when I fetched it, so the
response-request reading depends on the petition docket's mirror entry.
