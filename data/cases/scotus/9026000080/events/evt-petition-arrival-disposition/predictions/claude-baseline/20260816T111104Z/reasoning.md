# Reasoning — why these numbers

**P(grant family) = 0.004.**

*Anchor.* This is an arrival-moment cert cell: `record/context.json` freezes
`band: baseline` under `sal-v3`, matching the statpack band table's version, so
the anchor is the baseline band's bracketed `reached` rate — the whole paid
scored segment's rate, unconditional on trajectory, which is exactly the
arrival population's figure. Pooled over the table's Terms strictly before this
petition's (OT2017–OT2025, n ≈ 13,163 weighted), that is ≈ 6.5%.

*Adjustments down, large and compounding:*

- **Pro se petitioner.** The petition is paid (`sJsonCaseType: Paid`) but filed
  by the petitioner herself, not counsel. The Court essentially never grants
  plenary review on a pro se petition; the paid-segment anchor is dominated by
  counseled petitions.
- **Pure error correction.** All three QPs contest the application of settled
  standards (Anderson/Tolan summary-judgment review, McDonnell Douglas
  burden-shifting, pro se forfeiture) to this record. No circuit split is
  alleged anywhere in the petition — the "Reasons for Granting" cite only this
  Court's own precedent.
- **Response waived.** The city waived its response on Aug 6, 2026. The Court
  does not grant without a response on file, so the grant path requires a CFR
  first — an extra low-probability step the docket shows no sign of.
- **Thin vehicle.** A 9-page petition describing the disputed facts only
  generally, with typographical and citation errors (e.g., Tolan v. Cotton
  misreported at 512/572 U.S. 650).

*Adjustment up, small:* the Fifth Circuit's opinion is published and, per the
petition, drew a dissent concluding summary judgment was improper. A published
panel dissent on a Tolan-style light-most-favorable question is the one feature
that occasionally produces a summary reversal or GVR even without counsel. It
keeps my number off the floor rather than moving it materially — I could not
verify the dissent independently (see `retrieval.md`), though the opinion's
published status checked out on CourtListener.

Landing point: ~0.4%, roughly a 15-fold discount from the paid-segment anchor,
consistent with the relist-0 bucket's grant+gvr rate (~1.7%) further discounted
for the pro se, splitless, waived-response posture.

**relist-increment = 0.97.** The frozen state is zero distributions, so this is
P(ever distributed). With the response waived the petition proceeds to
conference in ordinary course; the residual 3% covers dismissal or withdrawal
before any distribution (paid-segment dismissal runs ~1–2%, plus some
procedural attrition).

**cvsg-increment = 0.002.** No federal party or contested federal-program
interest; CVSGs go to counseled petitions where the United States has a stake.
Base CVSG incidence in the paid segment is ~1.3% and this petition sits far
below the segment average on every CVSG correlate.

**summary-disposition-route = 0.7 (conditional on grant).** Across the modern
slice the cert-order route is roughly half the grant family (gvr 576 vs
granted 674, with the caveat that the label split is unreliable across Terms).
Conditional on this fact-bound petition being acted on at all, the realistic
mechanisms are a Tolan-style per curiam summary reversal or a GVR — plenary
argument on a case-specific summary-judgment record is the least likely form
of a grant — so I set the conditional well above the unconditional cert-order
share.

**dissent-from-denial = 0.01.** Statements or dissents accompany on the order
of a percent of denials, concentrated in counseled petitions raising issues a
Justice is campaigning on. The pro se, generally-pleaded record makes a writing
unlikely even though the subject (summary judgment in discrimination cases) is
one that has drawn separate writings before.

**Uncertainty and discounts.** My biggest uncertainty is the Fifth Circuit
dissent: I could not read the opinion (the CourtListener opinion record for
this cluster carries mismatched text from an unrelated case), so I am taking
the petition's characterization on faith. If the dissent is as described — a
published dissent squarely on genuine disputes of material fact — a GVR-adjacent
outcome is somewhat more live than my 0.4% implies; if it is narrower, less.
Corpus citation-filter retrieval returned nothing (a documented coverage gap,
not evidence of no precedent). The statpack sections I anchored on are the
sal-v3 band table (version match confirmed) pooled strictly over pre-OT2026
Terms, and the relist/CVSG cuts read as shape only.
