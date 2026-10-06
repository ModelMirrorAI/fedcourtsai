# Rationale for the numbers

**P(grant) = 0.20; predicted disposition `denied`.**

## What I read

Provisioned inputs: the snapshot `record/snapshots/2026-10-05.json` (twelve
docket entries through the Sep 9 reply; paid; Term 2025 docket number
25-1383; petitioners' counsel of record at Skadden, respondents' at a New
Orleans firm), `record/context.json` (forward mode, band `baseline` under
sal-v4, one distribution, no CVSG, Term 2025), and all three provisioned
documents: `questions-presented.txt`, the full 61-page `petition.txt`, and the
full 39-page `brief-in-opposition.txt`. None was flagged `empty_text`, and
`documents.json` shows none truncated. The reply brief of Sep 9 was not
provisioned and I did not retrieve it.

## Anchor

Cert stage, `moment: distribution`, band `baseline` frozen at prediction, so
the anchor is the bracketed **reached** rate for `baseline` in the statpack's
"Segment base rate by salience band (sal-v4)" table, pooled over Term rows
strictly before this case's Term (2025). The table renders ten Terms and 2026
is empty, so the pool is 2017 through 2024:

| Term | reached rate | n |
| --- | --- | --- |
| 2024 | 5.7% | 1271 |
| 2023 | 5.9% | 1312 |
| 2022 | 5.8% | 1192 |
| 2021 | 5.6% | 1500 |
| 2020 | 4.5% | 1739 |
| 2019 | 4.6% | 1399 |
| 2018 | 4.6% | 1524 |
| 2017 | 4.7% | 1643 |

Pooled: about 593 grants over 11,580, roughly **5.1%**. The salience version
in the table heading (sal-v4) matches my context's `salience_version`, so the
band table is a valid anchor. Cross-checks from the paid scored-segment cuts:
relist bucket 0 shows a 1.7% grant family (terminal count, which understates a
live petition's prospects), bucket 1 shows 13.3%; CVSG `none` shows 6.3%; the
Fifth Circuit's modern cert row shows a 3.7% grant family.

## Adjustments upward

1. **The Court called for a response after a waiver.** This is the strongest
   signal on the docket and the salience band does not encode it. A call for a
   response means at least one chambers thought the petition worth a look; a
   large share of grants from waived petitions pass through this step, while
   most called-for petitions are still denied. I treat it as roughly tripling
   the anchor, to the mid-teens.
2. **Petition quality.** Counsel of record is a leading Supreme Court
   advocate. The question presented is one the Court expressly reserved in GE
   Energy (590 U.S. at 445), which gives the petition a hook most do not have.
   The Fifth Circuit's opinion is published (161 F.4th 282), the panel was
   unanimous, and rehearing en banc was denied, so the conflict is settled on
   that side.
3. **The split is real and now reasoned on both sides.** The petition counts
   four circuits applying federal common law (First, Second, Fourth, Ninth)
   against the Fifth. The BIO's best authority, the Seventh Circuit's Kim v.
   Jump Trading (Aug. 13, 2026, Easterbrook, J.), as the BIO quotes it, holds
   that estoppel under Chapter 2 is governed by state law through § 208 and
   Arthur Andersen. That is a second circuit on the Fifth's side with a
   reasoned opinion, which makes the conflict harder to describe as a
   one-court aberration. I could not read Kim directly (see below), so this
   rests on the BIO's own quotation of it.
4. **Two cert-stage amici** (the property-casualty trade association and a
   group of international arbitration scholars and arbitrators), a modest
   stakes signal, and a recurring issue: the petition cites a dozen Louisiana
   district court decisions on the same estoppel route and twenty-odd state
   statutes restricting insurance arbitration.

Together these put the petition in roughly the top decile of paid petitions,
where I would expect something like a 25-30% grant rate.

## Adjustments downward

1. **The vehicle objections are substantial and specific.** The BIO shows that
   no live claim exists against either foreign insurer (three respondents
   never sued them, the fourth dismissed them with prejudice before service),
   so even the intertwined-claims form of estoppel petitioners want may fail
   on its own terms; that the respondents are public entities against whom
   estoppel runs differently; and that petitioners do not challenge the
   separate-contracts holding, so the Convention reaches the case only through
   estoppel. Petitioners' answer is Bufkin, where the same Fifth Circuit
   applied concerted-misconduct estoppel on parallel facts, but that answer is
   weakest for the three respondents who never sued the foreign insurers. A
   Court that agrees the question matters can still find this an awkward case
   to answer it in.
2. **The insurance overlay.** McCarran-Ferguson, a Louisiana statute voiding
   insurance arbitration clauses, and the Louisiana Supreme Court's Police
   Jury decision make the case unrepresentative of Convention disputes
   generally. The Court has let the Louisiana hurricane-insurance arbitration
   petitions pass before.
3. **A cleaner vehicle is coming.** Kim was decided in August 2026, so a
   petition there could be filed by late 2026. The Court often waits for the
   case without the complications.
4. **The merits lean toward the decision below.** The § 208 route (Chapter 1
   applies absent conflict; GE Energy found the Convention silent; Hencely
   requires a significant conflict before federal common law displaces state
   law) is textually tidy. The Court grants more readily when it expects to
   reverse.

Net: **0.20**. I hold this with moderate confidence; a reasonable range is
0.12 to 0.30.

## The other claims

- **relist-increment 0.97.** The one distribution shown was superseded by the
  call for a response. The petition will be redistributed now that the reply
  is in, which adds a distribution entry whatever the Court then does. The
  residual 0.03 covers an unusual docket path (withdrawal, settlement, or a
  disposition entered without a fresh distribution line).
- **cvsg-increment 0.18.** A treaty-adjacent question on which the federal
  government has views and a Court unsure of the vehicle. Not the modal path.
- **summary-disposition-route 0.03** (conditional on grant). No intervening
  decision; nothing to GVR against.
- **dissent-from-denial 0.07** (conditional on denial). No committed
  dissenter on this issue; a short statement respecting denial is the only
  plausible writing.
- **big_case_score 0.3.** Technical but with real industry stakes.

## Uncertainties and where to discount me

- I could not read Kim v. Jump Trading. CourtListener's text for the opinion
  is font-encoding garbage in both the opinions endpoint and the document
  reader, so my characterization of its holding comes from the BIO's
  quotations. If Kim is narrower than the BIO presents it, the split is
  shallower on the Fifth Circuit's side and the grant case weakens slightly.
- I did not read the Sep 9 reply brief, which presumably addresses Kim and
  the "no claims against foreign insurers" point. My read of how well
  petitioners answer the vehicle objections is inferred from the petition and
  the Fifth Circuit's Bufkin decision as both briefs describe it.
- The corpus priors surface was unhelpful for this question: the citation
  filter has no coverage (the corpus notes only 200 SCOTUS rows carry any
  cite), and a scan of eighty recent granted rows turned up no arbitration or
  insurance captions. The statpack is the only corpus-side anchor I used.
- Corpus freshness: the statpack is the committed `metrics/statpack.md` on
  this checkout; I did not run `corpus-info` in the cell. The live docket I
  fetched from supremecourt.gov today matches the snapshot through the Sep 9
  reply with nothing after it, so the snapshot is current as of prediction
  time.
- I checked the live docket for this case in forward mode, as the prompt
  permits. It shows no disposition, so the cell is not mis-provisioned.
