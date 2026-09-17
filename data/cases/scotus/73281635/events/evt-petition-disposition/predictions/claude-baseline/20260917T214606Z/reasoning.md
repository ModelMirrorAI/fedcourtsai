# Rationale for the numbers

**P(grant) = 0.09, predicted disposition `denied`.**

## What I read

- Provisioned snapshot `2026-09-17.json` (10 docket entries, paid docket
  25-1146, Seventh Circuit No. 24-1674, no capital marking).
- `record/context.json`: mode `forward`, band `elevated` under `sal-v4`, Term
  2025, `distribution_count` 2, no CVSG, `cutoff` null.
- `record/documents/`: `questions-presented.txt`, `petition.txt` (62 pp., text
  extracted), `brief-in-opposition.txt` (37 pp., text extracted). No document
  carried `empty_text`. The petitioners' reply (July 31) was not provisioned
  and I did not fetch it.
- The Seventh Circuit opinion (Kolar, J., joined by Brennan, C.J., and
  Maldonado, J.; 158 F.4th 879), read through the CourtListener MCP server in
  forward mode. It is unanimous, with no separate writing.
- `metrics/statpack.md`: modern-cert base rate, the relist-count and CVSG
  cuts, and the sal-v4 segment table.

## Anchor

The context's band is `elevated` under `sal-v4`, and the statpack's segment
table is also `sal-v4`, so the table is my anchor. Pooling the bracketed
`reached` figures for `elevated` over the eight Term rows strictly before
Term 2025 (2017 through 2024, weighted by their `n`) gives roughly 17% (about
484 weighted grants over about 2,810 weighted petitions that reached the
band). That is the yardstick the evaluator will score against.

The relist-count cut's bucket `2` (granted 27.8%, gvr 13.1%) is *not* an
appropriate reading for this docket. The second distribution here is a
call-for-response redistribution: the petition was distributed for May 28,
the Court requested a response on May 20 before that conference, and it was
redistributed for the September 28 long conference once briefing closed. It
has never actually been considered at conference, so in substance it sits at
zero relists, and the statpack caption itself warns the stored count is an
upper bound on true relists. The signal that *is* real in that sequence is
the call for a response after respondent waived, which is a genuine mark of
interest and is presumably part of what put the petition in `elevated`.

## Adjustments from the anchor

Downward, and the reasons are substantive rather than stylistic:

1. **The asserted split is thin, and the record says so twice.** The petition
   claims a 3-versus-6 split. The Seventh Circuit's footnote and the BIO both
   show the three "no interest" circuits do not hold what the petition needs:
   the Third Circuit's statement is a footnote of dicta in a FELA case whose
   holding was that FELA allows no prejudgment interest at all (Poleto); the
   Fourth Circuit in Gilliam reversed on the facts (the jury award already
   reflected delay and past/future damages could not be disaggregated) and
   expressly left room for interest on a different record; the Tenth Circuit
   in White merely affirmed a discretionary denial as not an abuse of
   discretion. No circuit has adopted the categorical bar the petition asks
   the Court to impose. The Court very rarely grants on an "important
   question" alone when the petitioner's own authorities do not squarely
   hold for it.
2. **The QP is overbroad relative to the Court's method.** The question asks
   for an across-the-board rule for all federal claims, but the Court's
   prejudgment-interest doctrine (Rodgers, West Virginia, City of Milwaukee)
   is statute-by-statute. The BIO presses this hard and notes the petitioners
   never made a Section 1983-specific argument below, so the narrower question
   is unpreserved.
3. **Posture.** The Seventh Circuit remanded for apportionment of the award
   between past and future damages, so the interest figure is not final. The
   Court can and does take cases in this posture, but it is one more reason
   to deny a petition that is otherwise marginal.
4. **Asymmetry of advocacy.** Respondent is represented by a highly
   experienced Supreme Court practitioner; the BIO is well constructed and
   attacks the split, the vehicle, and the merits in that order. The petition
   is filed by the City's own law department.

Upward, but less than the downward factors:

1. **The Court called for a response after a waiver.** That is an affirmative
   act of attention by at least one chambers and is the strongest signal on
   this docket.
2. **Practical stakes and an institutional petitioner.** The City of Chicago
   faces a stream of large wrongful-conviction verdicts, the interest here was
   $7.6 million on a $25 million award, and the International Municipal
   Lawyers Association filed in support. Municipal exposure is a recognizable
   cert theme.
3. **Genuine outcome tension.** Whatever the doctrinal labels, Gilliam
   (Fourth Circuit) and this case are both wrongful-conviction Section 1983
   verdicts of purely noneconomic damages, and the interest award was
   reversed in one and largely upheld in the other. A Justice interested in
   remedial uniformity could see that as enough.
4. **Long-conference timing with full briefing.** The petition arrives at the
   September 28 conference fully briefed with a reply, which is where paid,
   responded-to petitions tend to fare best.

Net: I land at 0.09, roughly half the band anchor. My prior for a paid
petition on which the Court has called for a response after a waiver is on the
order of one in ten grants, and this petition's split and vehicle problems put
it below the middle of that population, while the institutional stakes keep it
from falling to the docket's baseline rate.

## The other claims

- `relist-increment` 0.28: nearly all grants come after a relist, so this is
  bounded below by the grant probability; I add the chance of a relist ending
  in denial, which for a call-for-response petition at the long conference is
  meaningful but not the modal outcome.
- `cvsg-increment` 0.04: no federal party or federal program at stake; the
  federal government's own prejudgment-interest exposure is statutory.
- `summary-disposition-route` 0.04 (conditional on grant): no intervening
  decision and a unanimous, well-reasoned opinion below; if the Court grants
  it will be to hear the case.
- `dissent-from-denial` 0.05 (conditional on denial): a technical remedial
  question with no Justice's known agenda attached.
- `big_case_score` 0.25: real money for municipalities, but a narrow, dry
  question with limited public salience.

## Uncertainties and where to discount me

- I do not know what feature of sal-v4 placed this docket in `elevated`; if it
  was the two-distribution count rather than the call for response, the band
  anchor overstates this docket's position more than I have assumed.
- I did not read the petitioners' reply brief, which may answer the BIO's
  "no split" argument better than the petition does.
- My rough recollection of grant rates conditional on a call for response is
  from general knowledge, not from a committed statpack cut; the statpack has
  no response-requested cut for cert petitions.
- Retrieval was light (two corpus queries, four MCP calls). Nothing I
  retrieved disclosed this petition's disposition; CourtListener's SCOTUS
  docket search for 25-1146 returned no rows.
- The corpus query with a free-text argument was rejected by the tool
  (structured filters only); the two structured queries returned recent
  granted and denied SCOTUS rows that were general context rather than
  topical priors, and I did not lean on them.
