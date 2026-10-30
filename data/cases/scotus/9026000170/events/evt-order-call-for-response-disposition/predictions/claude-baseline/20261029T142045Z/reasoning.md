# Reasoning — P(grant) = 0.06

**Inputs read.** Snapshot `record/snapshots/2026-08-29.json` (cut `date`,
cutoff 2026-08-29), `record/context.json` (forward mode, band `baseline` under
`sal-v4`, distribution_count 1, no CVSG), `record/documents/questions-presented.txt`
and `record/documents/petition.txt` (87 pages, not truncated, not OCR). No brief
in opposition exists yet — the Court has just called for one — so my read of
the opposition is inference, not text.

**Anchor.** Statpack "Segment base rate by salience band (sal-v4)", `baseline`
column, bracketed `reached` rate over OT2017–OT2025 (the Terms strictly before
OT2026): 4.9, 4.8, 4.7, 4.5, 5.7, 5.9, 5.9, 5.9, 4.0% on n≈1,200–1,750 a Term,
pooling to about **5%**. Petitioner is private (FedEx), so `baseline` is also the
caption-class floor; the band and the floor agree. Cross-checks: Federal Circuit
origin in the modern-cert cut runs granted 3.0% + gvr 1.6% (n=900 resolved),
roughly in line.

**Adjustments.**
- *Up* for the call for a response. It shows at least one chambers (or the
  pool) thought the petition merited a response, and paid petitions with a
  called-for response grant at a materially higher rate than waived ones. But
  no committed table conditions on it, and the bar is low; I treat it as
  roughly doubling the base, not more. The petition is well-lawyered
  (Finnegan) and frames an agency-admitted statutory violation.
- *Down* for the merits/vehicle picture. *Thryv* (2020) already held the
  § 315(b) institution bar unreviewable under § 314(d); the RPI requirement is
  if anything more closely tied to institution, and the Federal Circuit's
  exclusive patent jurisdiction means no split can develop. The Office has
  changed its prospective policy (dedesignated *SharkNinja* / *Unified*),
  which the SG will press as removing ongoing importance, and the Office has
  also re-centralized institution decisions, shrinking the future footprint.
  The United States as respondent will oppose — the SG's opposition is a
  strong deny signal for a private petitioner against the government.

Net: about 0.06, i.e. slightly above the band anchor — the call-for-response
lift mostly offset by the *Thryv* overhang and the SG's expected opposition.

**Claims.** `relist-increment` 0.97 (masked on this moment; another
distribution after the response is all but certain). `cvsg-increment` 0.005 —
the US is a party, so a CVSG is structurally near-impossible.
`summary-disposition-route` 0.15 given a grant — no intervening decision; a
GVR could arise only if the SG's concession of error turned into a confession
inviting remand, which its § 314(d) position makes unlikely.
`dissent-from-denial` 0.06 — Justice Gorsuch's *Thryv* dissent makes a written
dissent conceivable, but he has generally not written on denials in this
line; `order-writers` puts most of that mass on him, consistent with the
claim.

**Uncertainty / discount.** I have not seen the responses; a response that
unexpectedly fails to defend the judgment (e.g. the SG suggesting remand)
would move this sharply. Corpus priors (`fedcourts query`) returned nothing
case-specific — the citation column is sparse — so the number rests on the
statpack and my own reading of the § 314(d) line. No outcome or post-cutoff
material was sought or seen.
