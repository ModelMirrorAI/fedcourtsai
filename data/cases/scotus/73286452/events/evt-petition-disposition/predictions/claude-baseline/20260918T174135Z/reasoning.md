# Why 0.40

## Inputs

I read the provisioned snapshot `record/snapshots/2026-09-17.json` (18 docket
entries through the August 26, 2026 redistribution), `record/context.json`
(forward mode, band `elevated` under `sal-v4`, `distribution_count` 2, no CVSG,
Term 2025), the event definition, and all three provisioned documents:
`questions-presented.txt`, `petition.txt` (29 pages, full text), and
`brief-in-opposition.txt` (25 pages, full text). None was `empty_text` or
truncated. I also read the committed `metrics/statpack.md`, ran one
`fedcourts query` for recent granted SCOTUS priors, and made five CourtListener
MCP calls (details in `retrieval.md`). I did not read anything under
`data/qp-topics/` and did not read this case's earlier-run predictions.

## Anchor

Cert stage, `moment: distribution`, band `elevated` frozen at prediction, so the
scored yardstick is the bracketed `reached` rate for `elevated` pooled over
Terms strictly before OT2025. The table's `sal-v4` heading matches the context's
`salience_version`. Pooling OT2017 through OT2024 (weighted by the bracketed n):
17.9% (336), 17.5% (354), 19.0% (300), 20.5% (342), 16.1% (397), 13.8% (334),
15.9% (347), 17.5% (400), which pools to roughly **17%** over about 2,810
petitions. The relist-count cut's bucket 1 (13.3% grant family) and the
originating-circuit cut for ca9 (about 3.2% grant family across all fee classes)
are consistent context but not the anchor.

One thing about the anchor worth saying plainly: under `sal-v4` the `elevated`
band encodes exactly one thing, a distribution count of 2. Here that second
distribution is the routine redistribution after the Court called for a
response and the brief in opposition arrived, not a discretionary relist. The
band's population includes petitions in the same position, so the anchor is
fair, but nothing in the band reflects the call for response, the amicus count,
or the en banc dissent. Those are the adjustments below.

## Adjustments upward (17% to about 40%)

- **The Court called for a response after the State waived** (June 11, 2026).
  That is an affirmative act by at least one chambers and is the single
  strongest signal on this docket. Called-for-response petitions grant at a
  multiple of otherwise-similar petitions.
- **Six cert-stage amicus briefs, including a multistate coalition led by
  Montana.** Amicus support at this volume at the cert stage is uncommon for a
  private petitioner and marks the case as one the conservative legal movement
  has organized around.
- **A three-judge dissent from denial of rehearing en banc** (VanDyke, joined
  by Bumatay and Tung, with a separate Tung dissent) that expressly says the
  panel is out of step with Supreme Court and sister-circuit precedent. The
  panel (Tashima, Nguyen, Mendoza; opinion by Nguyen) was unanimous. This is
  the Ninth Circuit configuration in which the current Court most often grants
  First Amendment petitions.
- **Subject matter.** A compelled-speech challenge to an implicit-bias
  curriculum mandate, resolved by expanding the government-speech doctrine to
  privately authored lectures, sits squarely in the current majority's First
  Amendment interests (NIFLA, 303 Creative, and Chiles v. Salazar, decided
  March 31, 2026). The petition's Matal v. Tam argument is strong on its face:
  the State does not write, edit, or pre-approve course content and delegates
  accreditation to private bodies.
- **Vehicle.** Final judgment, dismissal at the pleadings on a pure legal
  question, no standing or preservation problem apparent from either brief.
  Counsel (Pacific Legal Foundation with Consovoy McCarthy) are experienced
  Supreme Court advocates.

## Adjustments downward (why not higher)

- **The circuit split is thin.** The brief in opposition credibly argues that
  every cited circuit applies the same Shurtleff factors to different facts,
  and that no other circuit has addressed CME or comparable licensure
  instruction. The Court often waits for a true conflict on the specific
  regulatory form.
- **The panel disclaimed breadth.** The opinion calls its holding narrow and
  California-specific, and the State leans on that hard. The Court sometimes
  treats such a disclaimer as reducing the need for review even when it
  doubts the reasoning.
- **The State's merits response has some purchase.** Section 2190.1(e)(2)
  lets instructors teach "strategies" without affirming that implicit bias
  drives disparities, and the State cites a long history of topic-level CME
  content requirements (pain management, cultural competency) that would face
  strict scrutiny under petitioners' theory. A Justice worried about
  collateral consequences for ordinary CME regulation could prefer to let the
  issue percolate.
- **The Court just decided Chiles.** Having ruled for the professional speaker
  in March 2026, the Court may prefer to let lower courts absorb that decision
  before taking another professional-speech case, and a GVR in light of Chiles
  is a loose fit because Chiles did not address the government-speech
  threshold.
- **Docket size.** The Court has been granting fewer cases, and the
  long-conference denial rate is high even for well-supported petitions.

Weighing these, I land at 0.40. I would not defend anything above about 0.50 or
below about 0.28 on this record. Because 0.40 is below one half, the binary
point prediction is `granted: 0`, `predicted_disposition: denied`.

## The other claims

- **relist-increment 0.45.** Grants from the long conference are frequently
  announced without a relist, and a plain denial needs none, so a further
  distribution mostly comes from a Justice writing on a denial or one more look
  before a grant. P(relist | grant) about 0.6; P(relist | deny) about 0.3 given
  the dissent chance below; mixture about 0.42, rounded up slightly for
  reschedules, which also add a distribution entry.
- **cvsg-increment 0.03.** No federal party, statute, or program. Unsolicited SG
  participation would not count.
- **summary-disposition-route 0.25 (conditional on grant).** GVR in light of
  Chiles is conceivable but doctrinally loose; summary reversal of a published,
  unanimous opinion with a State respondent is rare. Plenary review is the
  likely grant route.
- **dissent-from-denial 0.35 (conditional on denial).** The issue, the amicus
  slate, and the en banc dissent make a Thomas or Alito writing plausible, but
  most denials of this kind still pass silently.

## Big-case score 0.55

Stakes if decided: the reach of the government-speech doctrine over privately
delivered, licensure-required instruction (CME and CLE nationwide), and the
constitutionality of implicit-bias training mandates that the State's brief
shows exist in several States. Significant First Amendment doctrine with a
culture-war valence, but a narrow class of regulation rather than a blockbuster.

## Where to discount me

The biggest uncertainty is how the Court weighs the call for response combined
with heavy amicus support against a thin split, and I have no corpus cut that
conditions on either the call for response or the amicus count; the adjustments
above are judgment, not measured rates. The `fedcourts query` I ran returned
mostly interim applications and recent grants unrelated to this subject, so it
contributed no comparable-prior evidence. I have no knowledge of this
petition's outcome; the next conference is September 28, 2026, after my
snapshot and after today's date, so the case is genuinely pending.
