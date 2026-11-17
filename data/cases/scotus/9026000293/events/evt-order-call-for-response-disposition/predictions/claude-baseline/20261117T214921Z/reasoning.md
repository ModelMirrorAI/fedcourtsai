# Reasoning — Ashton v. The Taliban, No. 26-293 (response-requested moment)

**P(any grant) = 0.32; predicted disposition: denied.**

## What the record shows

- Snapshot `2026-11-17.json` (forward mode, cutoff 2026-11-18). Paid petition from the Second Circuit (No. 23-444), filed Aug 31 2026. No respondent appeared; one amicus brief (Afghanistan's UN chargé d'affaires, VIDED across the three sibling dockets). Distributed for the Nov 6 conference, distributed again for Nov 13, then on Nov 16 the Court **invited the Solicitor General's views** (Justice Kagan recused), and on Nov 17 a **response was requested** (due Dec 17 2026).
- So although this cell is the response-requested moment, the stronger signal already on the record is the CVSG. The call for a response adds little on top of it: it reads as the Court wanting an adversarial paper on a docket where the respondents (the Taliban) never appeared.
- `record/related/`: 26-292 (*Havlish*, the Court's own `Vide` link) and 26-294 (*Owens*, `vided-amicus`, one shared brief; I read the docket and it is a true sibling from the same Second Circuit judgment). Both show the identical sequence: two distributions, CVSG Nov 16, response requested Nov 17. Havlish additionally has a multistate amicus brief (Iowa et al.) and a supplemental brief. The Court is treating the three petitions as a cluster.
- Petition (read from `petition.txt`; truncated in the appendix, body intact) and `questions-presented.txt`: this petition asks only for a **GVR in light of *Exxon Mobil v. Corporación CIMEX*** (June 2026) on the FSIA "foreign state" holding, and expressly joins Havlish's plenary arguments on the TRIA "blocking date" holding. It notes dissents from denial of rehearing en banc (Sullivan, joined by three; Menashi). `lower-court-docket.txt` says no en banc petition was found on CourtListener; the petition's own account (rehearing en banc denied over dissents) is the better source and I follow it. No decision-below text was staged.
- `same-question.json`: empty list — nothing to lean on.

## Anchors

- `cert_anchor.rate` = 0.350 (band `high`, sal-v8, ten prior Terms). `cert_amicus_line` (arm `some`) = 0.352.
- Statpack CVSG cut (paid scored segment): n=166 resolved, granted 29.5% + GVR 6.0% = 35.5% grant family. Relist bucket 2: 28.3% + 13.1% (n=498), though here the second distribution may be a reschedule/relist before the CVSG.
- No committed table conditions on a called-for response; I treat it as roughly neutral given the CVSG already on the docket.

## Adjustments

This petition's fate is mostly derivative of Havlish (26-292), the lead vehicle.

- P(the Court grants plenary review in the cluster) ≈ 0.40: slightly above the CVSG base rate because of the en banc dissents, an asserted TRIA timing conflict with the Ninth and Eleventh Circuits, state amici, and very large stakes; held back because the decision below is deferential to the Executive's recognition power (a position the Solicitor General may well defend, and CVSG outcomes track the SG's recommendation closely), there is no adversary respondent, and the facts are unusual enough to be read as one-off.
- Given a cluster grant, this petition ends in the grant family ≈ 0.7: either granted and consolidated (it comes from the same judgment and asks for consolidation), or held and later GVR'd if the petitioners prevail; a hold followed by denial if the judgment is affirmed is the loss branch.
- A stand-alone GVR in light of *Cimex* ≈ 0.04. As the petition itself describes *Cimex*, it concerned whether the Helms-Burton Act displaces FSIA immunity, not whether Executive recognition fixes "foreign state" status; the link to the holding below is by methodology, which is a thin basis for a Lawrence v. Chater GVR. I did not independently verify the petition's account of *Cimex*.

0.40 × 0.70 + 0.04 ≈ 0.32 — just under the band anchor, because this is the tag-along petition rather than the lead one.

## Other claims

- `relist-increment` 0.97: a further distribution after the response/SG brief is near certain (short of a withdrawal/dismissal).
- `cvsg-increment` 0.02: a CVSG is already on the docket; the claim is vacuous here.
- `summary-disposition-route` 0.60 (conditional on grant): most of my grant mass for this docket is a GVR (after a hold, or directly), the rest a consolidated plenary grant.
- `dissent-from-denial` 0.08 (conditional on denial): after a CVSG and with en banc dissents below, a statement is more plausible than usual but still uncommon. Kagan is recused, so her writing probability is near zero.

## Where to discount me

- I do not know what the Solicitor General will say; that is the largest single driver and I am guessing at its direction.
- The hold-then-GVR branch depends on a merits outcome in a case not yet granted.
- No retrieval beyond the provisioned inputs, the statpack, and one corpus query (which returned generic GVR rows of no specific use).
