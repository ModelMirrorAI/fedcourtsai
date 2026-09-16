# Why 0.15, and where to discount me

## Mode, inputs, and the state I forecast from

Forward cell, `band: baseline` under `sal-v4`, `distribution_count: 1`, Term
2025, paid docket No. 25-1269 out of the Third Circuit. I read the provisioned
snapshot `record/snapshots/2026-09-16.json`, `context.json`, the petition and
questions-presented text in `record/documents/`, and `event.yaml`
(`moment` unspecified, kind `petition`, so the cert stage governs). The
snapshot shows: petition filed May 4, 2026; respondent waived June 9;
petitioners' supplemental brief June 16 and distribution for the September 28
conference June 17; **Response Requested July 15**; response time extended to
September 14; brief in opposition submitted September 14. No CVSG.

## Anchor

The prompt's anchor for a `baseline`-band paid petition is the bracketed
`reached` rate pooled over Term rows strictly before 2025 in the statpack's
"Segment base rate by salience band (sal-v4)" table. Pooling OT2017 through
OT2024 (n from 1,192 to 1,739 per Term, rates 4.5% to 5.9%) gives roughly 5%.
That is the evaluator's yardstick. The salience band did not register the
call for a response (the context's `response_requested` is null and the band
is `baseline`), so the anchor understates this docket's signal and I move
well off it.

## Adjustments up

1. **The call for a response.** After the respondent waived, a chambers asked
   for a response two months after *Jules* came down. The Court's working
   rule is not to grant (GVRs included) without a response, so a CFR after a
   waiver means at least one Justice or the pool memo saw a live possibility
   of relief. My recollection of the empirical literature is that paid
   petitions with a CFR grant on the order of one in ten, several times the
   paid base rate; the corpus statpack publishes no CFR cut, so this is a
   remembered figure, not a committed one, and a reader should weight it
   accordingly.
2. **The ask is a GVR, and the lead case is decided.** *Jules v. Andre Balazs
   Properties*, No. 25-83, was decided May 14, 2026, unanimously, holding that
   a federal court that stayed a pending suit under FAA section 3 keeps
   jurisdiction to confirm or vacate the resulting award under sections 9 and
   10, and closing with the line that nothing in the FAA "precludes the normal
   operation of federal jurisdiction regarding live claims that are still
   pending before a federal court." That is the direction petitioners needed,
   and the Court GVRs liberally under *Lawrence v. Chater*'s "reasonable
   probability" standard when a petition ties the decision below to a
   just-clarified precedent. The panel's Part IV did read *Badgerow* against
   petitioners' "jurisdictional anchor" theory, which is the passage a GVR
   would cite.
3. **Counsel.** Petitioners are represented by Kellogg Hansen (Derek Ho), a
   repeat Supreme Court practice; the petition and supplemental brief are
   tightly drafted around the GVR ask.

## Adjustments down

1. **The panel's operative ground is independent of *Jules*.** I read the
   Third Circuit opinion (petition appendix 1a to 21a). Its holding is that a
   section 1782 application is not a "civil action" within section 4's own
   text, reasoned from the Field Code lineage of that term, the Federal
   Rules, the 1954 amendment history, and the removal-statute case law; Part
   IV rejects the "anchor" argument chiefly because petitioners never
   reconciled it with section 4's text, and footnote 52 declines even to say
   whether the "civil action" limit is jurisdictional. *Jules* addressed
   sections 9 and 10, expressly contrasted section 4's "distinctive" look-
   through language, and never asked what counts as a "civil action." The
   brief in opposition makes exactly this point, cites *Wellons v. Hall*'s
   dissent on GVRs where the decision below is independently supported, and
   reframes the question presented as the narrow "civil action" one. I find
   that reading of the opinion correct, which is the main reason I stay
   under 0.2 despite the CFR.
2. **No split, first impression, rarely recurring.** The panel called the
   appeal "unusual" and said the question "will not often recur"; respondent
   says no other circuit has faced it. Plenary review is therefore a rounding
   error (about 0.02 of my 0.15).
3. **Vehicle problems.** The arbitration clause seats arbitration in London,
   and section 4 allows a court to compel arbitration only "within the
   district" of filing, an independent bar under Third Circuit precedent
   (*Control Screening*); petitioners' Chapter 2 argument was held waived;
   and a second Third Circuit appeal on a renewed motion to compel is
   pending, so even a sympathetic Court has a later, cleaner opportunity.
4. **The dispute's character.** A litigation funder resisting section 1782
   discovery sought by its former counterparty, with serial *Coinbase* stays;
   the brief in opposition's account of delay will not endear the petition to
   the Justices who decide GVRs, even if the equities do not formally bear on
   *Lawrence*.

Netting these, I put the GVR near 0.13 and plenary grant near 0.02, so
P(any grant) = 0.15 and `predicted_disposition` = `denied`.

## The other claims

- `relist-increment` 0.93: the June 17 distribution for September 28 has been
  overtaken by the CFR and the September 14 BIO; a new distribution entry for
  an October conference is close to certain once the reply is in, and the
  claim resolves on the distribution count rising above one. The residual
  covers a parse that folds the redistribution into the existing entry or a
  disposition off the September 28 list without a new entry.
- `cvsg-increment` 0.03: no federal interest, and a GVR request is not a CVSG
  candidate.
- `summary-disposition-route` 0.9 conditional on grant: the petition asks for
  a GVR and nothing else; the statpack's modern-cert GVR share of the grant
  family sits near half, and this docket's shape pushes far above that.
- `dissent-from-denial` 0.04 conditional on denial: narrow, tangled, no
  visible chambers interest.
- `big_case_score` 0.12: low stakes beyond the parties and the litigation-
  funding bar.

## Uncertainties and discounts

- The CFR-conditional grant rate is a remembered figure; the corpus publishes
  no such cut. If the true CFR-conditional GVR rate for hold-for-a-decided-
  case petitions is materially higher than one in ten, I am too low.
- I could not read the pool memo's view. A Justice inclined to police lower-
  court readings of *Badgerow* could carry a GVR over the BIO's objection, and
  GVRs are cheap; that is the bulk of my 0.15.
- The brief in opposition and the supplemental brief were **not** in the
  provisioned `record/documents/` (the document fetch predates them); I
  retrieved both from supremecourt.gov, together with the petition appendix
  for the Third Circuit opinion, and the *Jules* opinion from CourtListener.
  A predictor working from the provisioned inputs alone would not have seen
  the BIO's vehicle arguments.
- I did not read the prior claude-baseline run's output for this event
  (July 17, 2026) and forecast from this moment's record only.
- Corpus priors: one `fedcourts query` for 2020s SCOTUS GVR rows returned 20
  priors, all June 29 and 30, 2026 end-of-Term GVRs with distribution counts
  of 2 to 4 and none flagged as response-requested; useful only as a shape
  check (GVRs cluster at Term's end and after at least one redistribution),
  not as a matched comparison.
