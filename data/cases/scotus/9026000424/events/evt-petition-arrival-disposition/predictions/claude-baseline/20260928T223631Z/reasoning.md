# Rationale for the numbers

**P(grant) = 0.004.**

**Anchor.** `record/context.json` freezes `band: baseline` under `sal-v4`,
`term: 2026`, `distribution_count: 0`, no CVSG, `mode: forward`. This is an
arrival cell, so per the prompt I anchor on the caption class's own floor
rather than any distributed-population figure. The petitioner is a private
individual (Beckie Boddie, pro se; the respondent, a federal court, does not
change the petitioner's class), so the class is `private` and the floor is
`baseline`'s bracketed `reached` rate. Pooling every prior Term the statpack's
"Segment base rate by salience band (sal-v4)" table renders (OT2017 through
OT2025; the OT2026 row is empty) gives a weighted `reached` grant rate of
about 5.0% over n = 12,720. The statpack's own version (`sal-v4`) matches the
context's, so the table is a valid anchor and no mismatch flag is owed.

**Adjustments downward, and why they are large.** The baseline floor covers
every paid private petition, including counselled petitions with real
questions presented. This petition is at the far weak end of that population
on every observable dimension:

- **Posture.** The caption names the district court as respondent, and
  CourtListener shows the Fourth Circuit matter (No. 26-1130) is "In re: Beckie
  Boddie", a mandamus petition resolved by informal briefing and an unpublished
  per curiam opinion with judgment on April 9, 2026. Certiorari to review a
  denial of mandamus against a district court is essentially never granted; the
  three petitions in the corpus's 2020s slice with a "v. United States District
  Court" caption were all denied.
- **Underlying dispute.** The originating case is D. Md. No. 1:18-cv-03309-PX,
  In re Sanctuary Belize Litigation, the FTC's receivership over a Belize real
  estate scheme. Boddie's filings there are a 2024 "Petition: Right of Victim as
  Third Party to Petition the Court" and 2026 correspondence entries, so the
  grievance is a claimant's dissatisfaction with how the district court handled
  her submissions. That presents no legal question of general importance.
- **Pro se, paid.** The petitioner is her own counsel of record at a
  residential Las Vegas address. The fee class is paid (which is why the case
  sits in the paid scored segment at all), but pro se paid petitions grant at a
  small fraction of the counselled paid rate; the statpack has no pro se cut,
  so this adjustment is judgement rather than a published figure.
- **No adversary with a stake.** The Solicitor General appears only because a
  federal court is the nominal respondent and will waive; no brief in
  opposition will sharpen anything, and nothing here implicates the
  government's own interest in a way that produces a grant.
- **Record thinness.** No `record/documents/` directory was provisioned, so I
  have no questions presented or petition text. That is the ordinary state of a
  fresh arrival, not a defect, but it means the forecast rests on the caption,
  the lower-court posture, and the underlying docket rather than on the
  petition's own argument.

Together these move me from the 5% class floor to a number near the floor of
what a paid petition can plausibly carry. I put it at 0.4% rather than lower
because the Court occasionally GVRs or grants in unexpected shapes and I cannot
read the petition itself.

**Claims.**

- `disposition` 0.004: equals the top-level probability.
- `relist-increment` 0.95: the record shows zero distributions, so this is
  P(at least one distribution). Nearly every docketed paid petition is
  distributed once after the response is waived. The residual covers dismissal
  before conference (a Rule 14 or filing defect, a withdrawn petition, or the
  petitioner's failure to cure). The long gap between filing (July 6, 2026) and
  docketing (September 28, 2026) hints that the petition may already have been
  returned once for correction, which slightly raises that residual.
- `cvsg-increment` 0.001: the SG is already counsel for the respondent.
- `summary-disposition-route` 0.7: conditional on a grant, the realistic form
  would be a GVR or other cert-order disposition rather than argument; the
  prior Terms' cert-order share of grants runs roughly 30 to 60%, and this case's
  shape pushes well above that share because plenary review is inconceivable.
- `dissent-from-denial` 0.01: conditional on denial, no Justice is likely to
  write on a pro se mandamus petition of this kind.

**Big case score 0.03.** The Sanctuary Belize litigation itself was a large FTC
matter, but this petition concerns one claimant's procedural complaint and
would affect nobody else if decided.

**Uncertainty and where to discount me.** I have not read the petition, so if
it in fact raises a question about the rights of victims or third parties in
FTC receiverships in a way that maps onto a genuine split, I would be
underestimating it, though the mandamus posture would still make it a poor
vehicle. The underlying D. Md. entries were read from CourtListener's RECAP
mirror, which carries entry descriptions only; the documents themselves were
not available to read.

**Retrieval health.** The CourtListener MCP server and the corpus query service
both worked; no degradation. The corpus query surface has no caption or
free-text filter, so the mandamus-caption comparison above came from scanning a
400-row 2020s-era pull for "District Court" in the caption, and is illustrative
rather than a computed base rate. Corpus base rates came from the committed
`metrics/statpack.md`.
