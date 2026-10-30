# Reasoning — P(grant) = 0.004

**Inputs read.** Snapshot `record/snapshots/2026-10-30.json`; `record/context.json`
(mode `forward`, band `baseline` under `sal-v4`, distribution_count 1, no CVSG,
Term 2026); `record/documents/questions-presented.txt` and the opening of
`record/documents/petition.txt` (91 pages, not truncated, not OCR-derived; the
petitioner's contact details are withheld by the scrub). No brief in opposition
exists: the MSPB, through the Solicitor General, waived its response on Oct 23,
2026, and the petition was distributed on Oct 28 for the Nov 13 conference.

**Anchor.** The statpack's *Segment base rate by salience band (sal-v4)* table,
`baseline` column, bracketed `reached` figures for Terms 2017–2025 sit at
4.0%–5.9% (e.g. 2025: 4.0%, n=1314; 2024: 5.9%, n=1274), pooling to roughly 5%.
That figure is the private-petitioner class floor over all paid petitions,
including ones represented by the Supreme Court bar that later relist.

**Adjustments down, all strong.**
- *Pro se petitioner.* Paid but self-represented (counsel of record is the
  petitioner himself). Pro se paid petitions are granted far below the class floor.
- *Waiver by the SG and no call for response.* The great majority of grants follow
  a filed response; a petition denied on a waiver at first conference is the modal
  outcome.
- *Fact-bound questions.* QPs 1 and 3 ask whether particular disclosures about one
  position description were nonfrivolous allegations; QP 2 (continuing "failure to
  take" a personnel action) is the only legal question, and the petition claims no
  circuit split (its reasons section argues conflict with WPEA text and importance).
- *Nonprecedential Federal Circuit decision* affirming an MSPB jurisdictional
  dismissal.
- The `cafc` originating-court row (granted 3.0%) is dominated by patent
  petitions with counsel and is no help in raising this one.

Netting these, I put P(grant) at 0.4% — well under the 5% floor, essentially the
pro se paid rate. `relist-increment` 0.03 reflects the small chance the Court calls
for a response (which would redistribute the petition) or reschedules.
`cvsg-increment` 0.002: a CVSG makes no sense with the SG already the respondent's
counsel. `summary-disposition-route` 0.3, conditional on a grant, since any grant
here would most likely be a GVR/summary vacatur rather than plenary review.
`dissent-from-denial` 0.004: separate writing on a pro se whistleblower denial is
very rare. `order-writers` is kept consistent with that small figure.

**Uncertainty / discount.** I read only the front matter and question section of
the petition closely, not the full appendix; my view of vehicle quality rests on
the QPs, table of contents and the docket. Corpus `query` returned recent grants
(mostly SG-filed) that were not comparable priors; the forecast rests on the
statpack and the docket, not on retrieved priors. No CourtListener or web
retrieval was used.
