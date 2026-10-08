# Rationale for the numbers

**P(grant) 0.30; predicted disposition denied; granted = 0.**

## What I read

- The provisioned snapshot `record/snapshots/2026-10-08.json`: paid docket,
  Term 2026, Fourth Circuit Nos. 25-2199 and 25-2200 decided June 25, 2026;
  petition filed September 10 and docketed September 14, 2026; both respondent
  groups waived on September 21; petitioner's letter received September 24;
  distributed September 30 for the October 16, 2026 conference; October 6,
  "Response Requested" (due November 5, 2026); October 6, amicus brief of the
  Washington Legal Foundation submitted. Counsel of record: Kent Yalowitz,
  Arnold & Porter (petitioner); Jonathan Ellis, Sullivan & Cromwell, and Erik
  Zimmerman, Robinson Bradshaw (respondents).
- `record/context.json`: forward mode, band `baseline` under sal-v4,
  distribution_count 1, no CVSG, no cutoff, Term 2026.
- `record/documents/`: `questions-presented.txt` and `petition.txt` (38 pages,
  full text, not truncated). No brief in opposition exists yet, so none was
  provisioned.
- Beyond the record: the Fourth Circuit's published opinion (CourtListener
  opinion 11348682), the first pages of Tango Music (7th Cir. 2003), the
  petitioner's September 22 letter to the Clerk (extracted locally from the
  docket PDF), the Washington Legal Foundation's case page, and a civil
  procedure blog post on the decision below. See `retrieval.md`.

## What the filings show

The question is a single, clean statutory one. FS Medical, an LLC whose
members were citizens of Texas, California, and China, sued North Carolina and
United Kingdom defendants under section 1332(a)(3). The Fourth Circuit (Diaz,
C.J., joined by Wynn and Quattlebaum, unanimous, argued and published) held
that a dual-citizen LLC's foreign citizenship must be "tested" like any
member's citizenship, that doing so leaves no U.S. citizen on the plaintiff
side, and that paragraph (a)(3) therefore does not apply. It said the Seventh
Circuit's Tango Music "doesn't persuade us," characterized it as answering a
different question (same-country foreigners on both sides), and said that any
contrary holding gleaned from it is inconsistent with Grupo Dataflux.

The petition's split claim: Fourth Circuit versus Seventh Circuit (Tango
Music), plus an unpublished Fifth Circuit table decision (Leland, 1993,
concerning a dual-citizen corporation) and "tension" with the Second Circuit's
Windward Bora (a permanent-resident-member case). My own read of Tango Music's
opening pages confirms the Fourth Circuit's characterization is fair: Posner's
opinion states that "the U.S. parties are diverse" in one sentence and then
spends its analysis on whether U.K. citizens on both sides defeat (a)(3). The
lineup was materially identical to this case, so the result conflicts, but the
reasoning never engaged the point the Fourth Circuit decided. A strong brief in
opposition will say the split is one published holding against a passing
assumption, an unpublished table decision, and a different question, with a
district-court division underneath. That is a thinner conflict than the
petition's framing, though a real one on the result.

Vehicle points respondents will press: the Fourth Circuit's footnote 2 records
a third suit FS Medical filed without the Chinese member, pending on a section
1359 motion (the magistrate judge recommended dismissal); respondents will
argue the petitioner may yet have a federal forum and that the question need
not be decided here. Footnote 1 of the petition records an unresolved dispute
about whether Tanner Pharma UK is also a North Carolina citizen, which the
parties agreed is not germane. The Chinese member is a lawful permanent
resident domiciled in California, which the 2011 amendment to (a)(2) addresses
for individuals; it does not control (a)(3) but gives respondents a side
argument about how the question would arise on remand. None of these is a
disqualifying defect; the question was decided at every level on undisputed
citizenship facts and resolved the case.

## Anchor

The context band is `baseline` under sal-v4, matching the statpack table's
version, so the anchor is the bracketed `reached` rate for `baseline` pooled
over the nine Term rows strictly before Term 2026 (2017 through 2025, weighted
by the `n` beside each figure): about 5.0% (n about 12,720). That is the
yardstick this cell is scored against. For shape only: the relist-count cut's
one-relist bucket (two distributions) carries granted 8.2% plus GVR 5.1%, the
CA4 cut granted 1.3% plus GVR 1.2%, and the CVSG cut's `none` row granted 4.0%
plus GVR 2.3%; all are terminal-state cuts and none conditions on a call for
a response.

## Adjustments

The salience scorer reads relists, CVSG, and originating circuit only
(`docs/salience.md`), so the band does not see the October 6 call for a
response. That is the dominant signal on this docket and I adjust from the
anchor for it. Both respondents waived; the Court then asked for a response
before the first conference. A call for a response after a waiver means at
least one chambers wants the case opposed before voting, and among paid
petitions that draw one the grant rate is, in my experience of the docket,
on the order of ten percent, several times the waived-and-denied norm. That
alone takes the number from about 5% into the low teens.

Up from there, for features that make this petition stronger than the typical
called-for-response petition:

1. **A published, unanimous, argued circuit opinion that expressly declines to
   follow another circuit** on the meaning of a federal jurisdictional
   statute. The Court treats uniformity in jurisdictional rules as a reason to
   grant on thin splits (Hertz, Americold, and Lincoln Property were all
   granted on narrow conflicts about entity citizenship).
2. **Elite counsel on both sides.** Arnold & Porter's Supreme Court group (John
   Elwood and Allon Kedem on the brief) filed the petition; Sullivan &
   Cromwell will write the opposition. The Court will see the question framed
   and contested at the highest level.
3. **An amicus brief already filed** (Washington Legal Foundation) and the
   petitioner's letter asking that the petition be held for the amicus
   deadline, both signs of an organized effort rather than a one-off filing.
4. **The question is purely legal, resolved the case, and recurs** in the
   district courts, which the petition documents with about ten decisions
   since 2021 on both sides.

Down, for:

1. **The split is shallower than claimed.** Tango Music assumed the point
   rather than deciding it, Leland is unpublished and concerns a corporation,
   and Windward Bora is about a different member class. Respondents will
   argue there is one published holding and no conflict ripe for review.
2. **The Fourth Circuit's rule has textual force and district-court support.**
   The petition itself lists four district-court decisions on the Fourth
   Circuit's side; the Court may prefer to let the courts of appeals weigh in.
3. **The pending third suit** without the Chinese member gives respondents a
   "no practical need" argument and the Court an excuse to wait.
4. **The Court takes a diversity-jurisdiction case only every few Terms**, so
   the competition for the slot is real even when the question is clean.

Net: 0.30. I would put a reasonable range at 0.20 to 0.40; the midpoint
reflects that a called-for-response petition with an acknowledged
published-opinion conflict and top counsel is, in my judgment, about a
one-in-three grant, well above the band anchor but still a probable denial.
`granted` is 0 and `predicted_disposition` is `denied` because denial remains
the single most likely outcome.

## Claims

- `disposition` 0.30, as above.
- `relist-increment` 0.97. The frozen count is one distribution. The response
  request removes the petition from the October 16 conference, so the petition
  will be redistributed once the opposition and reply are filed; that entry
  alone resolves the claim true. The complement is a withdrawal or settlement
  before redistribution, which the stakes make unlikely in a two-month window.
- `cvsg-increment` 0.04. No federal interest; the Court's recent diversity
  cases were decided without a CVSG. Small residual for a Justice wanting the
  Solicitor General's view on a jurisdictional statute's structure.
- `summary-disposition-route` 0.04, conditional on a grant. No intervening
  decision for a GVR; the holding below is reasoned and published, so plenary
  review is the route if the Court takes it.
- `dissent-from-denial` 0.06, conditional on a denial. Technical jurisdiction
  questions rarely draw a writing on denial, but the call for a response shows
  at least one chambers' interest and a short statement respecting denial is
  possible.

## Big-case score

0.3. Within federal-courts practice the question matters (every LLC with a
foreign member in the Fourth Circuit is now outside diversity jurisdiction
when any foreign party is on the other side), and the underlying dispute is
large, but the case has no public salience beyond that.

## Where to discount me

- No brief in opposition exists yet. My account of respondents' arguments is
  inference from the Fourth Circuit's opinion and the petition's own
  concessions, not from their filing. A strong BIO on the depth of the split
  or on the third suit is the main downside risk to the number; a weak one is
  the main upside.
- The size of the adjustment for the call for a response is judgment: the
  statpack publishes no cut conditioned on it, and I have no committed figure
  for the grant rate among called-for-response paid petitions.
- I did not read the WLF amicus brief itself, only the Foundation's summary
  of it, and I did not read the Fourth Circuit's record on the third suit.
- The salience band is `baseline` and the evaluator scores skill against the
  baseline reached rate; a prediction this far above it is a deliberate
  departure, and if the Court denies without a relist the cell will score
  poorly against that anchor.
