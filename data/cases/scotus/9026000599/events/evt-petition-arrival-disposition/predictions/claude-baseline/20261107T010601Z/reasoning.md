# Reasoning: NPS v. National Trust for Historic Preservation (No. 26-599), arrival moment

**P(grant) = 0.88.** That counts any grant: plenary, GVR or summary reversal.

## Inputs
- Snapshot `2026-11-07.json`. It has one entry: the petition was filed Nov 5, 2026 and the response is due Dec 7. There are zero distributions and no CVSG, which is what defines the arrival moment.
- `petition.txt` (truncated at the cap, appendix included) and `questions-presented.txt`. The one QP asks whether the district court erred in enjoining the ongoing renovation of the White House East Wing.
- `lower-court-docket.txt`: CADC No. 26-5123, a published opinion issued Aug 7, 2026, with Judge Rao in dissent per the petition. No en banc petition was filed.
- `decision-below.txt` was provisioned, but I did not rely on it beyond the petition's account.
- No BIO yet. `same-question.json` lists nothing.

## Anchor
The petitioner is the federal government, with the Solicitor General as counsel of record. The arrival rule says to anchor on the caption-class floor, here `federal`. Pooling the `federal` bracketed reached rate over Terms 2017–2025 in the sal-v7 table gives about **73% (n≈212)**. The OT2026 row (n=4) is excluded because it is the case's own Term.

**Mismatch:** `context.json` freezes `band: "baseline"` and a `cert_anchor` of 0.0515. That is the private-class floor and does not match this caption, where the National Park Service et al. and the President are the petitioners. I flagged it (data-quality). My forecast uses the federal floor. Note that the cell will be scored against the 0.05 anchor.

## Adjustments up
- **On Aug 31, 2026 the Court granted the government's stay application (26A203) 5–4, with a per curiam opinion.** The stay was pending this very cert petition. The per curiam found the government likely to succeed on standing and the equities tipping its way. A stay pending cert requires a reasonable probability of a grant and a fair prospect of reversal, and five Justices have already found both. Petitions following a granted stay pending cert are granted in the large majority of cases.
- The stay order itself provides that it ends automatically if cert is denied. That gives the stay majority a concrete reason not to deny.

## Risks to the grant
- Mootness or a change in posture. The project is said to be about 70% complete, and the district court case may move on (final judgment, amended injunction). That could produce a dismissal or a denial. A Munsingwear vacatur would still count as a GVR, which is a grant.
- The Court could hold the petition or let it go once the stay has done its practical work. That would be unusual, though, with the SG asking for reversal.

## Route
The SG asks first for summary reversal or a GVR in light of the per curiam, citing Abbott v. LULAC (No. 25-845). That was an appeal, so it is a weaker analog for cert. Plenary review is the alternative. A Court split 5–4 with the Chief Justice in dissent may prefer full briefing to summarily reversing an elaborate published CADC opinion. But the per curiam was already detailed, so I set P(summary | grant) ≈ 0.5.

## Other claims
- relist-increment 0.97: some distribution is essentially certain.
- CVSG 0.005: the SG is the petitioner.
- Dissent from denial 0.55, conditional on a denial. A denial would most likely come through mootness or a changed posture, which could draw no writing. A contested denial would draw one from the stay majority.
- Order-writers: the mass sits on the stay dissenters (Roberts, Jackson, Sotomayor) because of the summary-reversal route.

## Discount me where
I did not read the full decision below. I have no BIO, so I cannot see whether the respondent will argue mootness. The stay opinion's analysis reached me only through the petition's appendix excerpt.
