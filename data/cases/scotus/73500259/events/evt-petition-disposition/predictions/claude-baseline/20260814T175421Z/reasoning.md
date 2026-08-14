# Rationale — P(grant family) 0.17

## Anchor

Forward cell, cert stage, `moment: distribution`. The frozen context
(`record/context.json`) carries `band: elevated` under `sal-v2`, which matches
the statpack's "Segment base rate by salience band (sal-v2)" table, so the band
table is my anchor. Pooling the **elevated** band's bracketed `reached` rates
over the Term rows strictly before this case's own Term (2025) — OT2017–OT2024,
n ≈ 3,411 weighted resolved — gives **≈ 20%**. That is the risk-set rate a live
petition that has reached this band actually faces, and the yardstick the
evaluator scores against. Cross-checks sit consistently: the paid-segment relist
cut at bucket 1–2 runs ~13–40% grant family, the CA9-origin cut is unremarkable
(~3.3% grant family unconditional), and the modern-cert overall rate is a few
percent — the band figure already folds the docket-progress signal in.

## Adjustments

**Up from the anchor:**
- **The Court requested a response** (June 15, 2026) after respondents had
  waived — an affirmative act of attention that the band derivation
  (distributions + CVSG) does not capture. Called-for responses are a classic
  precursor of serious consideration.
- **A genuine, acknowledged circuit conflict.** The Ninth Circuit's published
  opinion (163 F.4th 1272) expressly rejects the Seventh Circuit's Motorola
  analysis ("did not substantially grapple with the FTAIA's language"), on a
  recurring question — the Sherman Act's reach over foreign component purchases
  priced by U.S. negotiations — the Court has not addressed since Empagran
  (2004). The petition's split framing is at least colorable on the CA9
  opinion's own words.
- **Strong cert-stage apparatus:** experienced Supreme Court counsel on both
  sides (Paul Hastings; Sidley/Wilson Sonsini), a cert-stage amicus (ICLE), and
  stakes the defense bar will keep pressing.

**Down from the anchor:**
- **Serious vehicle problems, well-argued in the BIO.** Interlocutory
  summary-judgment posture; the Ninth Circuit remanded several potentially
  dispositive issues (the "did the RFQ prices truly bind" causation question,
  Seagate LLC's Illinois Brick control-exception indirect-purchaser claim, and
  an unreached import-effects exception), any of which could moot or blunt the
  QP.
- **The premise of the QP is contested.** The BIO's strongest point is that the
  panel disclaimed any negotiations-situs holding and rested on domestic price
  effects plus contractual price-binding — so the split may be narrower than
  billed, and the "unique facts" cabining gives the Court an easy pass.
- **The Court denied cert in Motorola itself** (No. 14-1122, June 15, 2015,
  confirmed via CourtListener), albeit pre-split and from the losing
  plaintiff's side.
- **Respondent equities:** NHK's guilty plea and its no-restitution deal
  premised on civil remedies make an unsympathetic petitioner.

Net: the response-requested signal and the quality of the conflict push above
20% on interest, but the vehicle and premise problems cut harder against an
actual grant of *this* petition. I land at **0.17**, essentially all of it
plenary grant — no intervening decision exists for a GVR, so the modal outcome
is **denied** and `granted = 0`.

## Claims

- `disposition` 0.17 — restates the above.
- `relist-increment` 0.45 — from the two-distribution state shown. Nearly all
  of the 0.17 grant mass implies a further distribution; the 0.12 CVSG path
  adds redistribution after the SG files; and relist-then-deny is common for
  petitions with a called-for response at the long conference. Slightly more
  likely than not the docket still ends at two distributions (clean deny on
  9/28), but it is close.
- `cvsg-increment` 0.12 — federal enforcement overlay (DOJ prosecuted the
  cartel; DOJ/FTC guidelines argued both ways) makes the SG's views a natural
  middle path; base-rate CVSG incidence is ~1% but this profile sits far above
  it. Coherence check: 0.12 × ~0.30 (statpack grant-family rate conditional on
  CVSG is ~36%, shaded down for the vehicle issues) plus non-CVSG grant mass
  ≈ 0.17 total.

## Uncertainties / where to discount me

- The biggest is how the Court reads the split: if it credits the BIO's
  narrowing of the CA9 holding, this is a fact-bound denial and 0.17 is too
  high; if it reads the CA9 opinion's express criticism of Motorola as the
  operative fact, 0.17 is too low.
- The relist-increment number is sensitive to a mechanical fact I cannot see:
  whether the June 25 distribution (mooted by the response request) behaves in
  resolution counting the way I assume. I forecast from the harness's frozen
  `distribution_count: 2` as instructed.
- All three provisioned documents (petition, QP, BIO) carried extracted text
  (`empty_text: false`, untruncated); the reply of Aug 5 is on the docket but
  not provisioned, so my read of petitioners' answer to the vehicle arguments
  is inference, not text.
- Corpus retrieval added little beyond the statpack: a `fedcourts query` for
  recent SCOTUS grants surfaced mostly interim applications, so my priors here
  rest on the committed statpack cuts plus the provisioned record.
