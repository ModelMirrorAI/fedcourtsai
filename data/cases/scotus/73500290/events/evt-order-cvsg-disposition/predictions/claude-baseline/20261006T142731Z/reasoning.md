# Why P(grant) = 0.41

**Cell.** Forward-mode cert cell at the CVSG moment. Snapshot
`2026-10-06.json` (cut kind `date`, cutoff 2026-10-06), band `high` under
`sal-v4`, docket-number Term 2025, distribution count 1, CVSG dated
2026-10-05. Paid petition, CA6, private petitioner, Paul Clement counsel of
record.

**Anchor.** The committed statpack's *Segment base rate by salience band*
table is headed `sal-v4`, matching my context's `salience_version`, so the
`high` band's bracketed `reached` rate pooled over Terms strictly before 2025
is the yardstick. Pooling the eight rendered prior rows (2017 through 2024,
weighted by their n) gives 313.9 / 898, about **35.0%**. The paid-segment
CVSG cut agrees: granted 29.4% plus gvr 5.5%, a grant family of about 34.9%,
with denied 62.0% and dismissed 3.1% (n=163 resolved). I treat 0.35 as the
starting point.

**Adjustments up.**

- *A paired CVSG on the same question.* Through web retrieval (the
  CourtListener MCP server was rate-limited, see below) I found that
  *AstraZeneca v. Mosaic Health*, No. 25-1070, whose first question presented
  is the same Illinois Brick lost-profits question from the Second Circuit's
  side of the split, was distributed for the same September 28 conference and
  received a CVSG on October 5, 2026 (SCOTUSblog's docket mirror; the order
  list PDF itself could not be text-extracted on this runner). This predates
  my snapshot and is legitimate forward signal. It tells me the Court is
  interested in the question rather than merely in this case, and it opens a
  second route to a grant-family outcome here: a grant in No. 25-1070 with
  this petition held and later GVR'd if the Court confines Illinois Brick to
  overcharge pass-on.
- *The record below invites review.* Judge Bush's statement respecting denial
  of rehearing en banc says the case may warrant Supreme Court review; Judge
  Kethledge's panel concurrence called the result harmful to consumer
  welfare while feeling bound. The panel raised Illinois Brick sua sponte.
- *Vehicle and counsel.* Final judgment after a pleadings-stage dismissal of
  the antitrust claims; a precisely framed question presented; elite
  petitioner counsel. The petition names Second, Fourth, Ninth, Tenth, and
  D.C. Circuit authority on the other side.

**Adjustments down.**

- *The BIO's vehicle attack is substantial.* It argues (i) the Sixth Circuit
  also affirmed on ordinary proximate-cause grounds that the petition does not
  challenge, (ii) the joint-venture theory Judge Bush relied on was never
  pleaded and is forfeited, and (iii) the parallel state-law claims went
  through discovery to summary judgment on a record that undercuts the
  conspiracy narrative. I could not verify point (i) independently: the
  provisioned petition text truncates inside the panel opinion, the reply
  brief was not provisioned, and a secondary summary of the en banc writings
  describes no independent proximate-cause holding. The panel treats Illinois
  Brick itself as a proximate-cause rule, so (i) may be a characterization of
  the same analysis rather than a separate holding, but the SG will engage it,
  and SG denial recommendations often turn on exactly this kind of flaw when
  a second vehicle exists.
- *Two vehicles means this one may be the one left behind.* No. 25-1070 is
  interlocutory, which usually cuts against it, but it has a defendant
  petitioner, Chamber of Commerce amicus support, and no forfeiture problem.
  If the Court takes only one, the hold-then-deny branch for this case is
  real: if the Court extends Illinois Brick to lost-profit claims in the
  companion case, this petition is denied.
- *The SG may find the split shallow.* The BIO's "exceedingly shallow and
  undeveloped" framing is the SG's easiest path to recommending denial of
  both, and the Court follows an SG denial recommendation most of the time.

**Rough scenario arithmetic.** If the SG recommends a grant in at least one
of the two petitions (about even odds), I put this petition's grant-family
probability near 0.7 (plenary grant here or consolidated, plus roughly a 0.2
contribution from grant-in-25-1070 then GVR). If the SG recommends denial in
both, about 0.12. That blends to roughly 0.41 to 0.42. I commit to **0.41**.
The modal single outcome remains denial, so `predicted_disposition` is
`denied` with `granted` 0; the grant mass splits roughly 0.30 plenary and
0.11 GVR.

**Claims.**

- `disposition` 0.41, as above.
- `relist-increment` 0.96: a redistribution after the SG files is structural;
  the residual is settlement or withdrawal before the brief arrives, plus
  parse risk.
- `cvsg-increment` 0.01: a CVSG is already on the docket, so the claim is
  vacuous for this cell and the harness masks it; a second invitation does
  not happen.
- `summary-disposition-route` 0.28, conditional on a grant: above the CVSG
  cut's roughly 16% gvr share of the grant family because a specific
  companion-case GVR path exists here.
- `dissent-from-denial` 0.14, conditional on denial: most denial branches
  (SG recommends denial; held and denied after the companion case) are
  silent; a statement is plausible only if the Court denies both petitions
  and leaves the disagreement standing.

**Big-case score 0.45.** A genuine antitrust-standing question with paired
petitions and organized business interest, but technical and unlikely to draw
broad public attention even if decided.

**Where to discount me.** The CourtListener MCP server returned HTTP 429
(daily rate limit) on both calls, so I did not read the Sixth Circuit
opinions or the companion docket from the primary source; the companion
docket facts come from SCOTUSblog's case page and the en banc writings from a
law-firm blog summary. I did not read the reply brief. The corpus `query`
surface has no text filter, so the one query I ran returned recent granted
SCOTUS matters with no topical relation and did not inform the number. My
largest uncertainty is whether the respondents' alternative-ground argument
is real, which moves the SG's recommendation and this number by perhaps 0.1
either way. The horizon is long: the SG brief is unlikely before spring 2027,
and a hold behind No. 25-1070 would defer the disposition to 2028.
