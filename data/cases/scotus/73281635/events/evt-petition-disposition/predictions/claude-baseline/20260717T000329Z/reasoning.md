# Pesavento v. Bolden, No. 25-1146 — cert petition disposition

**Prediction: denied. P(grant, GVR included) = 0.10.**

## The case

Eddie Bolden served roughly 22 years on murder convictions that were vacated
for ineffective assistance; the State nolle prossed in 2016 and Bolden won a
section 1983 verdict of $25 million in compensatory damages (entirely
noneconomic — pain and suffering and loss of a normal life) plus punitive
damages against Chicago police detectives. The district court (N.D. Ill.)
added about $7.6 million in prejudgment interest. The Seventh Circuit
(158 F.4th 879, Nov. 6, 2025) adhered to *Hillier v. Southern Towing Co.* and
held prejudgment interest may be awarded on noneconomic damages, but reversed
in part: interest cannot run on *future* damages, so it remanded for the
district court to apportion the undifferentiated verdict between past and
future harm and recalculate. Rehearing en banc was denied Dec. 30, 2025. The
City of Chicago and the officers petitioned on a single pure question of law:
whether prejudgment interest is unavailable as a matter of law on noneconomic
damages.

## Grant-side signals

- **Call for response.** The respondent waived; the petition was distributed
  for the May 28, 2026 conference; and on May 20 the Court requested a
  response (BIO now due July 22, 2026 after an extension). A CFR means at
  least one chambers found the petition worth a closer look — empirically the
  strongest single signal on this docket, lifting the petition well above the
  paid-case base rate (roughly comparable to the corpus's 1-relist bucket,
  which grants at ~7.6% versus 0.8% for the no-signal bucket).
- **A colorable circuit split**, pressed with specificity: the Third
  (*Poleto*), Fourth (*Gilliam v. Allen*, a section 1983 wrongful-conviction
  case reversing prejudgment interest on noneconomic damages), and Tenth
  (*White v. Chafin*) versus the Fifth, Seventh, and Ninth (*Barnard*)
  allowing it, with the Second, Sixth, Eighth, and Eleventh allowing it in
  admiralty. *Gilliam* versus this case is a genuine, recent, same-statute
  conflict.
- **Institutional weight.** The City of Chicago petitions; the International
  Municipal Lawyers Association filed a petition-stage amicus; the petition
  documents a pipeline of district-court cases dividing on the issue in
  wrongful-conviction megaverdict litigation. Respondent retained top Supreme
  Court counsel (Paul Hughes, McDermott), signaling the defense bar and
  plaintiff bar both treat this as cert-worthy territory.
- **Clean legal question**, outcome-determinative for a ~$7.6 million award
  (reduced by agreement), preserved at every stage including a rehearing
  petition.

## Deny-side considerations

- **Interlocutory posture.** The Seventh Circuit remanded for apportionment of
  past versus future damages and recalculation of interest. The parties'
  April 2024 agreement resolved everything except prejudgment interest, which
  mitigates but does not eliminate the vehicle objection: the actual interest
  award is not yet fixed, and the Court routinely denies with the issue
  available on a later, final judgment. Expect the BIO to lead with this.
- **Split quality is contestable.** *Poleto* spoke in a footnote the Seventh
  Circuit called dicta; *Nance* is nonprecedential; *White v. Chafin* affirmed
  a *denial* of interest as within discretion (not a matter-of-law bar); even
  *Gilliam* reversed for abuse of discretion on its facts rather than adopting
  a categorical rule. The petition's own framing shows most contrary authority
  is admiralty-specific. A skilled BIO will characterize this as a shallow
  conflict about discretion, not a square matter-of-law split.
- **Low-salience remedies issue.** The Court takes prejudgment-interest
  questions rarely (*Milwaukee v. Cement Division* 1995, *Monessen* 1988), and
  federal-common-law interest standards are discretionary and fact-bound —
  the kind of question the Court often lets percolate further.
- **Base rate.** Modern paid discretionary petitions grant at a few percent
  (corpus statpack: ~2.5–3.3% per recent Term overall; CA7-originating
  petitions historically ~2.0%).

## Weighing

The CFR moves this petition out of the ordinary-denial mass, and the split
plus municipal-government interest make it a plausible eventual grant — but
the interlocutory posture and the contestable depth of the split are exactly
the flaws that convert "CFR'd and distributed" into "denied without comment"
or a percolation denial. Conditional on a CFR, grant probability for a paid
petition with a colorable-but-attackable split and a vehicle problem sits
around 8–12%; I set **P(grant) = 0.10** and predict **denied** as the modal
outcome. No GVR path exists (no intervening decision in view), and per-Justice
votes are not predictable from this record, so none are offered.

Timing note: the BIO is due July 22, 2026, so the petition will likely be
considered at the fall 2026 long conference or shortly after.

## Inputs relied on

- Snapshot `data/cases/scotus/73281635/record/snapshots/2026-07-16.json`
  (docket entries through June 16, 2026 — the CFR, waiver, extension, and
  distribution history above).
- Provisioned `questions-presented.txt` and `petition.txt` (62 pp.) — the QP,
  the split mapping, the statement of the case, and the vehicle claims. No
  brief in opposition exists yet (waiver, then extension to July 22, 2026).
- Committed `metrics/statpack.md` base rates and signal cuts (modern
  discretionary-cert disposition table, originating-circuit and relist/CVSG
  buckets, per-Term rates).
- CourtListener docket check confirming the petition remains pending
  (no cert grant/denial date, not terminated) as of this run.
