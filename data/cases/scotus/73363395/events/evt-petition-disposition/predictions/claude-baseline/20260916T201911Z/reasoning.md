# Rationale for the numbers

**P(grant) = 0.006.** The anchor is the statpack's sal-v4 segment table for the
`baseline` band, which `record/context.json` freezes for this cell
(`band: baseline`, `salience_version: sal-v4`, matching the table heading).
Pooling the bracketed `reached` rates over the eight Terms strictly before
this case's own (OT2017 through OT2024, docket 25-1292 is an OT2025 petition)
gives about 5.1% over a weighted n of roughly 11,600. That is the rate faced by
a paid private petition that has reached the baseline band, which is this
petition's situation as of its first distribution.

I adjust sharply downward from that anchor because this petition sits far
below the median baseline petition on every dimension the Court weighs:

- **The questions presented are foreclosed.** Both QPs assert a Seventh
  Amendment right to a jury trial in a Florida state-court civil action. The
  Seventh Amendment is not incorporated against the States, and the petition
  itself reproduces Florida Supreme Court language (In re 1978 Chevrolet Van)
  stating that the Seventh Amendment "is only binding upon federal courts."
  The due-process QP is the same grievance under another heading. The
  "Reasons for Granting" section (petition pp. 40-47) argues from Florida
  state cases and general quotations about the value of juries; it alleges no
  circuit split, no conflict with this Court's precedent, and no recurring
  question.
- **No federal question was decided below.** I read the Third DCA's published
  opinion (filed Jan. 2, 2025, No. 3D23-0802) via CourtListener. It is a
  straightforward state-law summary-judgment affirmance: Uber's uncontroverted
  records showed the driver had been logged off the app for nearly five months,
  and the plaintiff's two-phones theory was speculation that would require
  stacking inferences. The opinion does not mention the Seventh Amendment or
  due process at all, so the federal question appears to have been neither
  pressed nor passed upon in the state courts.
- **The respondent waived.** Uber filed a waiver of its right to respond on
  June 10, 2026. The Court does not grant without a response, so a grant
  would first require a call for a response, which nothing in this petition
  invites.
- **Filing posture.** The petition was first filed Jan. 22, 2026 but was not
  docketed until May 19, 2026, with a "Revised Petition" and "Corrected
  Appendix" and a motion to file a supplemental appendix under seal. That
  pattern usually reflects a deficient initial filing, a weak signal but one
  pointing the same way.
- **Originating court.** The statpack's originating-court cut shows the `fla`
  bucket at denied 99.6%, gvr 0.4% (n=232), with no plenary grants. This
  case comes from a Florida intermediate appellate court after the Florida
  Supreme Court declined jurisdiction, which is in the same family.

The 0.006 figure is essentially the residual probability of an outcome I
cannot foresee (an unexpected GVR in light of some decision I am not
anticipating, or a Justice deciding this is a vehicle for revisiting Seventh
Amendment incorporation). I do not think the true number is above 1%.

**relist-increment = 0.12.** Anchored on the state shown: one distribution,
for the 9/28/2026 long conference. The statpack's relist-count cut shows about
25% of the paid scored segment ending with more than one distribution entry,
but that is a terminal count that includes reschedules and response-driven
redistributions across all petitions, most of which are far stronger than this
one. For a petition with a waiver, foreclosed QPs, and no reason for a
response call, the realistic path to a second entry is an administrative
reschedule off the long conference, so I set the number well below the
population figure.

**cvsg-increment = 0.003.** No federal interest of any kind. The statpack's
CVSG cut shows about 1.2% of the paid segment ever draws a CVSG; this petition
is far below that population's median on federal salience.

**summary-disposition-route = 0.4 (conditional on grant).** The
population-wide cert-order share of the grant family in the modern-cert
disposition table is roughly 47% (gvr 577 against granted 655). For this case
the conditional cuts both ways: no intervening decision exists to GVR against,
but plenary review of these QPs is nearly inconceivable, so a grant, if it
happened, would probably be some summary action I am not foreseeing. I land
slightly below the population share.

**dissent-from-denial = 0.01 (conditional on denial).** No split, no recurring
question, no signaled interest by any Justice in a case of this shape. Kept
above zero only for the general base rate of statements respecting denial.

**big_case_score = 0.05.** A single wrongful-death vicarious-liability dispute
with a foreclosed constitutional framing. Seventh Amendment incorporation would
be significant if ever squarely presented, but this petition does not present
it, and a denial changes nothing for anyone but these parties.

**What I used.** The provisioned snapshot (2026-09-16.json; six proceedings
entries, one distribution, waiver filed, no CVSG), `petition.txt` (58 pages,
full text, read in full including the Reasons for Granting), and
`questions-presented.txt`. No brief in opposition exists because Uber waived;
`documents.json` lists only the petition and the QP cut. The committed
statpack supplied all base rates. Two `fedcourts query` calls returned mostly
substantive interim applications and one pending petition, none analogous, so
the corpus priors did not move the number. CourtListener retrieval (forward
mode, unrestricted) confirmed the docket is still open (no termination date,
last modified June 17, 2026) and supplied the Third DCA opinion text.

**Where to discount me.** My probability is an extreme one, and the main way
it is wrong is if the Court treats the petition as a vehicle for a question it
does not squarely present. I also could not read the Florida Supreme Court's
order declining jurisdiction or the trial-court orders (only the petition's
appendix descriptions of them), but nothing in the Third DCA opinion suggests
those would change the analysis.
