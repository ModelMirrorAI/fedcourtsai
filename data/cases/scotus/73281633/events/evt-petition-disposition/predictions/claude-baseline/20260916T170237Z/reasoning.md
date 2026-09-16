# Rationale for the numbers

**P(grant) = 0.11; predicted disposition `denied`.** Forward cell, mode
`forward`, snapshot `2026-09-15.json` read in full; documents read:
`questions-presented.txt`, `petition.txt` (statement, reasons for granting,
and the appended Second Circuit opinion's opening; the file is marked
`truncated: true` and cuts off inside the appended district-court opinion,
which cost me nothing that bears on the cert question), and
`brief-in-opposition.txt` (in full). The petitioner's reply brief (docketed
June 29, 2026) is not provisioned and I did not retrieve it.

## Anchor

`record/context.json`: `band: baseline`, `salience_version: sal-v4`,
`distribution_count: 1`, `cvsg_date: null`, `term: 2025`. The statpack's
"Segment base rate by salience band (sal-v4)" table matches the context's
version, so the band is my anchor. Pooling the **bracketed `reached`**
figure for `baseline` over the rendered Terms strictly before OT2025
(OT2017 through OT2024, weighted by their `n`) gives about **5.1%**
(roughly 593 grants over 11,580 weighted petitions; the per-Term rates run
4.5% to 5.9%). That is the yardstick the evaluator scores this cell against.
Cross-checks from the paid scored segment: the relist-count cut's `0`
bucket is 1.7% grant-family (but that is the rate among petitions that
*ended* undistributed-again, which understates a live petition), the CVSG
`none` bucket is 6.3% grant-family, and the CA2 originating-circuit row is
4.9% grant-family on the whole modern population.

## Adjustments up from 5.1%

- **Four cert-stage amicus briefs** (Pacific Legal Foundation, National
  Retail Federation, Manhattan Institute, Taxpayers Protection Alliance),
  all filed on the original response date. Cert-stage amicus support is one
  of the strongest observable grant correlates for a private petition, and
  it puts this petition well above the typical baseline-band member.
- **A colorable, citation-dense split claim on a recurring doctrinal
  question.** The petition frames a five-versus-two circuit disagreement on
  whether "common sense" can carry *Central Hudson*'s third prong (CA5
  *Bailey*, CA10 *Pacific Frontier*, CA6 en banc *Pagan*, CA9 *Junior Sports
  Magazines* against CA1 *Ayotte* and CA2), and a broader deference split on
  the fourth prong. The question *Greater New Orleans* expressly reserved and
  the *Borgner* dissent (Thomas, joined by Ginsburg) wanted answered is a
  real open question, and Justice Thomas's long-running interest in
  *Central Hudson* is a plausible source of a fourth vote.
- **The State filed a 42-page BIO** through its Solicitor General after two
  extensions rather than waiving, and the petition is paid with a national
  trade association as petitioner. The Court did not have to call for a
  response, which is a mild negative, but the respondent treated it as a
  serious petition.
- **Novelty of the regulatory form.** A sales restriction triggered by how a
  product is marketed is a shape the Court has not addressed, and the
  "speech as proxy for harm" theme has some pull with the current Court's
  First Amendment docket.

## Adjustments down

- **Interlocutory posture.** This is review of an affirmed denial of a
  preliminary injunction with the case proceeding to discovery below (the
  BIO reports both sides requested discovery and may offer experts). The
  Court's standard practice is to await final judgment, and *Central Hudson*'s
  third and fourth prongs are record-dependent in a way that makes a fuller
  record genuinely valuable. This is the single largest discount.
- **Alternative grounds below make the QPs non-outcome-determinative.** The
  district court held that petitioner's five-month delay eroded irreparable
  harm and that the public interest cut against relief, and the Second
  Circuit affirmed on those grounds too. The petition does not appear to
  contest them, so even a win on both QPs would not obviously change the
  result. That is a classic vehicle defect.
- **The split is contestable.** The BIO's account is plausible: the Second
  Circuit did cite studies and anecdotes and stated the *Edenfield* standard,
  so the disagreement reads as fact-bound application rather than a rule
  that evidence is unnecessary. The circuits on the other side all say
  "common sense" *can* suffice in the right case (quoting *Florida Bar* and
  *Lorillard*). A Justice looking for a clean legal question can fairly say
  there is none here yet.
- **Doctrinal climate.** *Free Speech Coalition v. Paxton* (2025) upheld an
  age-verification regime for minors under intermediate scrutiny with
  deference to the legislature's chosen means, and the Court has shown no
  appetite in recent Terms for revisiting *Central Hudson*'s rigor
  (*Sorrell* in 2011 sidestepped it). The heightened-scrutiny theme that
  would most energize a grant is, per the BIO, waived.
- **First distribution, Long Conference.** One distribution, no relist, no
  CVSG. The September 28 conference disposes of the summer's accumulation
  and grants a small absolute number; nothing in the docket yet marks this
  petition out from that pool beyond the amici.

Net: roughly double the pooled baseline-band rate. I land at **0.11**. I
would not go above about 0.18 without a relist or a response the Court
itself had called for, and not below about 0.06 given the amici.

## The other claims

- **relist-increment 0.32.** State forecast from: one distribution. Terminal
  buckets in the paid segment put roughly a quarter of petitions at one or
  more relists; this petition's amici and the state respondent raise the
  chance of one Long-Conference spillover, and every grant path and every
  separate-writing path passes through at least one relist. I read the
  hazard as about one in three for at least one more distribution, most of
  it a single relist.
- **cvsg-increment 0.03.** No federal party, no preemption QP, a state
  statute; the CVSG cut's population share is about 1.2% and I see only a
  faint FDA-adjacent reason to invite the SG. Slightly above population
  because the Court occasionally asks the SG on commercial-speech questions
  with federal regulatory overlap.
- **summary-disposition-route 0.08 (conditional on grant).** No intervening
  decision on point; a grant here means plenary review. The corpus-wide GVR
  share of the grant family is high, but that pool is dominated by
  criminal and federal-party petitions riding intervening decisions, which
  this is not.
- **dissent-from-denial 0.08 (conditional on denial).** Separate writings on
  denial are rare (low single digits among paid denials), but Justice
  Thomas's documented interest in exactly this question (*Borgner*,
  *44 Liquormart*, *Lorillard*, *Matal*) and the amicus attention make a
  statement or dissent more likely than for a random petition. Existence
  only; no per-Justice vote is recorded.

## big_case_score 0.45

Stakes if decided: a merits ruling would set the evidentiary and tailoring
burden for every commercial-speech restriction and reach the many recent
state laws regulating products or platforms marketed to minors. That is
doctrinally significant but not a headline case, and the concrete subject
(youth access to weight-loss supplements) is narrow. Scored on stakes, not
odds.

## Where to discount me

- I read the split through the parties' briefs and did not independently
  read the cited circuit opinions; if the CA6 en banc and CA9 decisions
  state an actual rule against "common sense" in the presence of studies,
  the split is stronger than I credit.
- I did not read the reply brief; if it squarely answers the
  non-outcome-determinative point (for example by showing the alternative
  grounds were themselves derivative of the merits), my largest discount
  shrinks.
- My sense of the Court's current appetite for commercial-speech cases is
  general knowledge as of my training, not a corpus measurement. The
  CourtListener check surfaced no other pending *Central Hudson* petition
  on the Court's docket, so I see no companion or hold candidate.
- Corpus priors from `fedcourts query` were not topically similar (the tool
  filters on structure, not subject), so the corpus contributed base rates
  through the statpack rather than analog cases.
- No outcome material was encountered: the petition is scheduled for the
  September 28, 2026 conference, and the live docket record showed no
  modification after July 1, 2026.
