# Why 0.25, and not higher or lower

## What I read

Provisioned inputs: `record/snapshots/2026-10-05.json` (the full supremecourt.gov
docket for No. 26-208 as of today), `record/context.json` (forward mode, band
`baseline` under sal-v4, `distribution_count` 1, no CVSG, Term 2026),
`record/documents/petition.txt` (43 pages, text extracted cleanly, read in
full) and `questions-presented.txt`. There is **no brief in opposition** yet:
the government waived on Sep 14 and the Court requested a response on Sep 29
(due Oct 29, 2026), so everything I say about the opposition is inference
about what the Solicitor General will argue, not a reading of what it argued.
`event.yaml` confirms a cert-stage, `moment: distribution` cell, so the
`cert-v2` five-claim set applies.

## Anchor

The frozen band is `baseline`. Pooling the band's bracketed `reached` rate
over the statpack's rendered Terms strictly before this one (OT2017 to OT2025,
n about 12,700 weighted) gives roughly **5%**; the single most recent Term
(OT2025) reads 3.9%. That is the yardstick this cell is scored against, and
my starting point. For shape I also read the relist-count cut (relist-0
petitions: granted plus GVR about 1.7%; relist-1: about 13%), the CVSG cut
(irrelevant here, the government is respondent), and the originating-circuit
cut (CA5 grant family about 3.7% of resolved petitions).

## Adjustments up (from about 5% to about 25%)

1. **The Court called for a response after a waiver.** This is the strongest
   signal on the docket and it is not in the band or in any statpack cut. From
   general knowledge of the cert process, a Court-requested response moves a
   paid petition from well under 1% (waived, no request) into the high single
   digits or low teens; it means some chambers flagged the petition at the
   pool-memo stage. I weight this heavily.
2. **Ten amicus briefs at the cert stage**, from a broad coalition (ABA, Cato
   and Freedom of the Press Foundation, Constitutional Accountability Center,
   Fourth Amendment scholars, Rutherford Institute, PPSA, Haitian Bridge
   Alliance, TCDLA, ADC, Prof. Cloud). Cert-stage amicus support is a
   well-documented grant predictor, and ten is far above the ordinary.
3. **A real, acknowledged split** (6-2 on whether a warrant is ever required,
   2-1 on suspicion for forensic searches), which the United States itself
   described as entrenched and important when it was the petitioner in Cano.
4. **Elite counsel** (Tutt, Jones, Elwood, Pacific Legal Foundation) and a
   petition written to the Court's current Fourth Amendment vocabulary (Riley,
   Carpenter, and the 2026 Chatrie decision the petition cites).
5. **A cleaner vehicle than the earlier denials**: a civil challenge with no
   exclusionary-rule, good-faith or harmless-error overlay, and a lower-court
   opinion that expressly calls the QP dispositive.

## Adjustments down (why not 40%+)

1. **The Court has denied this exact question three times** since 2021 (Cano,
   Merchant, Anibowei I), including once at the Solicitor General's own urging.
   Issue-specific history is strong evidence that the Court is content to let
   this percolate or is waiting for a particular vehicle.
2. **Vehicle objections the SG will press**: the district court's 5 U.S.C. 704
   adequate-remedy holding (the Fifth Circuit declined to affirm on it but
   did not reject it, leaving an alternative ground); standing for prospective
   relief against a policy; and the demanding standard for a facial challenge
   to directives that already require reasonable suspicion for advanced
   searches. The Court typically prefers a concrete search in a criminal case.
3. **The split is arguably narrowing on manual searches** (Fourth Circuit,
   Belmonte Cardozo 2026) while **Second Circuit appeals are pending** (Smith,
   Robinson) that could produce a sharper, more recent conflict, both of
   which hand the SG a percolation argument.
4. **Unpublished, four-page opinion below.** Usually a vehicle negative; here
   diminished because the panel rested on published circuit precedent and
   framed the question cleanly, but still a mark against.
5. **The response request is a necessary, not sufficient, signal.** Most
   petitions with a requested response are still denied.

Netting these, I land at **P(grant) = 0.25**, `granted` = 0,
`predicted_disposition` = `denied`. A reader who thinks the Court is finally
ready to take this question should sit nearer 0.35 to 0.40; a reader who
weights the three prior denials and the facial-challenge posture more than I
do should sit nearer 0.15. I would not defend anything below 0.10 given the
response request plus the amicus count, nor anything above 0.45 given the
issue history and the absence of the government's brief.

## The other claims

- `relist-increment` 0.97: a requested response makes a redistribution for a
  later conference essentially mechanical; the residual is a dismissal or
  withdrawal before then.
- `cvsg-increment` 0.01: the United States is the respondent; the SG is
  already counsel of record. The claim is effectively vacuous but a
  probability is required.
- `summary-disposition-route` 0.04 (conditional on grant): nothing to GVR in
  light of; no summary reversal of six circuits. The statpack's grant-family
  shows GVRs as a large share of grants in general, but that share is driven
  by intervening-decision GVRs that have no analogue here.
- `dissent-from-denial` 0.30 (conditional on denial): earlier denials on this
  question drew no writing, which holds it down; the response request and
  amicus coalition push it up.
- `big_case_score` 0.72: stakes are high and broad if decided; see the
  rationale field.

## Where to discount me

- No brief in opposition exists, so the strength of the vehicle objections is
  my guess at the SG's brief, not a reading of it.
- The response-request effect is priced from general knowledge of the cert
  process, not from a committed statpack cut; the harness has no baseline for
  it and I flagged that in `flags.json`.
- Corpus retrieval was thin: `fedcourts query` cannot filter on question
  presented or caption, and the citation filter is unpopulated on SCOTUS rows,
  so I could not pull the earlier border-search petitions as priors.
  CourtListener's SCOTUS docket index returned nothing for them either. My
  account of those denials (Cano, Merchant, Anibowei I) rests on the petition's
  own statement of related cases and on general knowledge.
- I do not know this petition's outcome; it is pending with the response not
  yet filed. Nothing retrieved touched its disposition.
