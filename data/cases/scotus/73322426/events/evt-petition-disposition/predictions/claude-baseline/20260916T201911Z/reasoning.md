# Rationale for the numbers — Johnson v. Montana, No. 25-1273

**P(any grant) = 0.15**, predicted disposition `denied`, `granted = 0`.

## What I read

Provisioned inputs: the snapshot `record/snapshots/2026-09-16.json` (created
2026-09-15 upstream, seven docket entries through the September 15 reply),
`record/context.json` (forward mode, band `baseline` under sal-v4,
`distribution_count` 1, no CVSG, Term 2025), the petition text
(`petition.txt`, 30 pages, fully extracted) and `questions-presented.txt`.
`documents.json` lists no brief in opposition or reply: the documents were
fetched on 2026-07-17, before either existed. Because this is a **forward**
cell with unrestricted retrieval, I fetched both from the URLs the snapshot's
own docket entries carry (supremecourt.gov) and extracted their text locally;
the BIO (86 pages with supplemental appendix) and the 13-page reply are
therefore inputs to this forecast, not inferences from the docket. Anyone
comparing predictors in this fan-out should know the other cells may not have
read them.

## Anchor

The context froze band `baseline` under `sal-v4`, which matches the version
the statpack's "Segment base rate by salience band (sal-v4)" table was
computed under, so that table is my anchor. Pooling the bracketed `reached`
figure for `baseline` over every rendered Term strictly before OT2025
(OT2017–OT2024, weighted by the risk-set `n`) gives **about 5.1%**
(n ≈ 11,600). That is the rate a once-distributed paid petition that had
reached the weakest band actually faces, and it is the yardstick this cell is
scored against.

Other statpack cuts I read for shape: the relist-count cut (relist bucket 0:
1.2% granted, 0.5% GVR; bucket 1: 8.2% granted, 5.1% GVR; bucket 2: 27.8%
granted) and the CVSG cut (no CVSG: 4.0% granted, 2.3% GVR). Both bucket by
terminal state, so they describe where petitions end up, not the hazard from
my vantage. The modern discretionary-cert section puts the grant family
(granted + GVR) at roughly 2.8% of resolved petitions overall.

## Adjustments up (why 15% and not 5%)

1. **The Court called for a response.** Montana waived; on July 6 the Court
   requested a response. A call for a response is not a feature of the
   sal-v4 band vocabulary (the band stayed `baseline`), so it is signal the
   anchor does not price. Empirically, paid petitions on which the Court
   calls for a response are granted at a substantially higher rate than the
   waived population — on my reading of the public commentary, in the range
   of one in six to one in ten — while a waived, uncalled petition grants
   around 1%. This is the largest single adjustment; I treat it as moving the
   anchor to roughly 12–15% before considering the merits of the petition.
2. **Petition quality and counsel.** The UCLA Supreme Court Clinic (Stuart
   Banner) is a repeat Supreme Court advocate; the petition is tight, the
   question presented is a single clean legal question, and the decision
   below is published (584 P.3d 77) with an express holding that "the proper
   test for remote witness testimony is the two-prong test first set out in
   Craig."
3. **The tension is real and widely acknowledged.** The petition collects a
   dozen courts describing a "tension" or "contradiction" between Craig and
   Crawford, Chief Judge Sutton's Cox concurrence asking this Court to
   resolve it, two state high courts (Missouri, Michigan) applying Crawford to
   adult two-way-video testimony, the Second Circuit's own Gigante standard,
   and Justice Sotomayor's Wrotten statement calling the question "important"
   and "not obviously answered by Maryland v. Craig." The Court has shown
   recent appetite for Confrontation Clause cases (Smith v. Arizona, 2024),
   and the originalist wing has an evident interest in Craig's reliability
   balancing.
4. **Dispositiveness on the standard.** The Montana court found the witness
   *available*, so under Crawford the state loses on the standard; the choice
   of test decides the constitutional question, which is a good vehicle
   property.

## Adjustments down (why 15% and not 30%)

1. **Preservation.** The BIO shows, with the appellant's brief in its
   supplemental appendix, that Johnson argued below only that Craig's two
   prongs were unmet and never argued Crawford displaced Craig. The reply's
   answer — the Montana court addressed the Craig/Crawford question sua
   sponte, so it is preserved under Adams v. Robertson, and Yee lets a party
   make new arguments in support of a preserved claim — is respectable, and
   the opinion's "we clarify and reaffirm" language helps it, but the Court
   is reluctant to grant where a state petitioner switched theories.
2. **Harmlessness.** Johnson testified at trial that he entered the garage
   without permission and hid there, and a trooper arrested him inside the
   house. Even accepting the reply's Coy point that Maw's testimony must be
   excised, the remaining evidence on the burglary count looks strong. The
   Court routinely denies where a grant would not change the outcome, and
   the Neder "remand harmlessness" practice does not make it eager to take
   such a case.
3. **Unsympathetic posture for petitioner.** The witness was 86, caring for
   his wife and adopted children, 450 miles away, and had moved during a
   delay caused by Johnson's own failure to appear (hence the bail-jumping
   count). The invited-error argument is weak as law, but these facts make
   this an unattractive case in which to announce a strict rule.
4. **The Court's track record on this exact question.** It denied Wrotten
   (2010) and Weigand (2023) and has let Craig stand for 36 years; a
   lopsided split (two state high courts against, by the BIO's count,
   twenty-five appellate courts and eight circuits) on a question the Court
   has declined before is often left to percolate further. Pitts v.
   Mississippi (2025), which applied Craig without controversy in a
   child-witness case, cuts mildly toward the Court being content with the
   Craig framework, though the reply is right that Pitts did not present
   the adult two-way-video question.

Net: the call for a response and the petition's quality lift this well above
the 5% anchor; the vehicle problems and the Court's history of passing on the
question keep it below one in four. **0.15.**

## Claims

- `disposition` 0.15 — same belief as the headline.
- `relist-increment` 0.94 — the snapshot shows one distribution (June 24,
  for the September 28 conference) that the July 6 call for a response
  superseded. With the reply submitted September 15, a redistribution entry
  is essentially certain; the residual is dismissal or withdrawal before it
  posts, or a redistribution the harness's count does not register.
  I also expect (about 55%) at least one relist after first consideration,
  but the claim resolves on any further distribution, so the number is the
  redistribution probability.
- `cvsg-increment` 0.04 — state prosecution, no federal party; the federal
  interest in remote-testimony standards is real but the Court has not sought
  the SG's views on this question before.
- `summary-disposition-route` 0.05 (conditional on grant) — no intervening
  decision to GVR against; the Court would not narrow or overrule Craig
  summarily. The statpack publishes no cert-order share I could anchor on for
  this Term window, so this is judgment.
- `dissent-from-denial` 0.15 (conditional on denial) — a Wrotten-style
  statement respecting denial is plausible given the call for a response and
  at least two Justices' evident interest in the question, but most
  called-for-response denials are silent.

## Uncertainties and where to discount me

- The size of the call-for-response effect is the crux, and I hold it from
  general knowledge of the paid docket rather than from a statpack cut; the
  pack has no response-requested cut, and the band vocabulary does not carry
  the signal. If the true conditional grant rate after a call for a response
  is nearer 8% than 15%, my number is a few points high.
- I have not read the Montana Supreme Court opinion itself, only the
  petition's and BIO's accounts and CourtListener's metadata (a single
  combined opinion authored by Justice McKinnon, no separate writing
  listed). Whether the opinion "expressly addressed" the Craig/Crawford
  choice is exactly the preservation question, and I am relying on the
  quoted passages.
- No amicus support is on the docket; for a question the petition calls
  nationally important, that is a mild negative I have folded in.
- `big_case_score` 0.55 reflects the doctrinal reach of the question if
  decided, not the odds of a grant.

## Retrieval and tooling notes

CourtListener MCP was available (three calls). One `fedcourts query` for
recent granted SCOTUS priors returned mostly application dockets and a few
relisted cert grants, useful only as a contrast profile. No outcome-revealing
material was encountered; the case is pending.
