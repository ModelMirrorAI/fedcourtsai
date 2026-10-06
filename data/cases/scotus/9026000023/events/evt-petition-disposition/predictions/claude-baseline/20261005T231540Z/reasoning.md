# Rationale for the numbers

**P(grant) = 0.07; predicted disposition denied.**

## Anchor

`context.json` freezes `band: baseline` under sal-v4 for a private petitioner (TMX Finance Corporate Services, a Texas/Georgia back-office company; Pennsylvania's Secretary is the respondent, so no caption-class uplift applies). The statpack's "Segment base rate by salience band (sal-v4)" table renders OT2017 through OT2025 ahead of this OT2026 docket. Pooling the baseline band's bracketed `reached` figures over those nine Terms (weighted by their `n`, 12,720 petitions in total) gives about 5.0%. That is my anchor. The modern-cert whole-docket rate (granted plus GVR about 2.8% of resolved) and the CA5 originating-circuit cut (granted 1.6%, GVR 2.1%) sit below it, as expected for a paid petition.

## Adjustments upward

- **The Court called for a response after a waiver** (Aug 12 2026). That is the one affirmative signal on this docket. Conditional on a call for a response, paid petitions grant at several times the band rate; I treat it as moving the number toward roughly 0.10.
- **A companion petition is on the identical track.** No. 25-1359 (TitleMax of Virginia v. Spicher, from the Third Circuit) was filed Jun 3 2026, drew a waiver, then a response request on Jul 29, and now has a response due Nov 2 2026, the same day as this one's. South Carolina filed an amicus brief there. Two petitions on one question from two circuits, with a state amicus and aligned response dates, read as the Court taking the issue seriously enough to want Pennsylvania's answer.
- **Counsel of record is an experienced Supreme Court advocate** and the petition is well built: it anticipates the Court's attention to interstate regulatory reach (Suncor was argued Oct 5 2026) and offers a hold behind 25-1359 as an alternative.
- **The 2022 denial in TitleMax of Delaware v. Vague (No. 21-1262)** rested, per the petition, on the respondent's point that only an investigation was pending. An enforcement action with a $52.7 million penalty demand is now pending, so that vehicle objection is gone.

## Adjustments downward

- **The asserted split has largely collapsed on these facts.** The petition's split rests on the Fourth Circuit (Harper) and the Tenth Circuit against the Third, Fifth, and Seventh. On Aug 5 2026, after the petition was filed, the Fourth Circuit issued a published opinion in TitleMax of South Carolina v. Spicher (No. 25-2027) applying Harper's own framework to this same Pennsylvania order-to-show-cause proceeding and holding the important-state-interest factor satisfied: Pennsylvania's usury enforcement against loans to its residents, with liens recorded and vehicles repossessed in Pennsylvania, is "different than in Harper," and no circuit precedent marks the interest as suspect. Every circuit that has looked at this proceeding (Third, Fourth, Fifth) has abstained. The brief in opposition will lead with this, and the Court routinely treats a methodological disagreement with a uniform bottom line as no split. This is the largest single factor and pulls the number back below the response-requested level.
- **Vehicle.** The Fifth Circuit opinion is unpublished and seven pages. The petitioner never made a loan and is the weakest-contacts entity in the family, which makes a good due-process story but a poor vehicle for a Younger holding about regulating out-of-state lending. If the Court wants the issue, 25-1359 is the better vehicle, and this petition's own best case is a hold.
- **Underlying merits are weak after National Pork Producers.** The Third Circuit already rejected the dormant Commerce Clause theory in Weissmann (2022), and the Fourth Circuit's opinion leans on that. A Justice weighing whether the abstention question is worth a grant will see little federal-claim upside at the end of it.
- **Younger grants are rare.** Sprint (2013) is the last time the Court took the doctrine's scope, and the Court has shown no appetite since.

Net: start near 0.05, move up to about 0.10 on the response request, companion, and counsel, then down to about 0.07 on the Fourth Circuit decision, vehicle, and merits. I hold 0.07 and would not defend anything outside 0.05 to 0.10.

## The other claims

- **relist-increment 0.96.** The frozen count is 1, but that distribution was withdrawn the same day by the response request; a re-distribution after Nov 2 is near-certain under the `dist-v2` reading that counts distribution entries. The residual is withdrawal or dismissal before re-distribution (the Pennsylvania proceeding could settle or end). This number says nothing about pre-grant relisting; see `flags.json`.
- **cvsg-increment 0.05.** No federal interest in play; a CVSG on a Younger question against a State is unusual.
- **summary-disposition-route 0.40 (conditional on grant).** The hold-then-GVR path behind 25-1359 is a large share of this petition's grant mass; a consolidated plenary grant is the rest. The statpack's prior-Term cert-order share of grants (GVRs run 30 to 59% of the grant family where the label is populated) is consistent with that split, and the companion structure here pushes toward GVR rather than away from it.
- **dissent-from-denial 0.08.** Younger denials rarely draw writings; the published Fourth Circuit affirmance gives a sympathetic Justice a reason to wait.

## Big case score

0.35. The issue matters to federal-courts doctrine and to the interstate regulatory fights the petition invokes, but it is procedural, the petitioner is a title-lender affiliate, and a decision would draw practitioner rather than public attention.

## What I used and where to discount me

I read the provisioned snapshot (`2026-10-05.json`), the petition and its questions-presented cut (`documents.json` shows both extracted, no truncation), `context.json`, and the statpack. No brief in opposition exists yet. I retrieved the Fourth Circuit opinion from CourtListener and the companion docket from supremecourt.gov (CourtListener holds that docket as an empty shell); both postdate the petition and predate the snapshot, so they are legitimate forward signal, and I have disclosed them in `flags.json`. The Fifth Circuit's opinion is not indexed on CourtListener, so my read of it is the petition's account and the Fourth Circuit's summary. `fedcourts query` returned no usable priors (the citation filter is nearly unpopulated on SCOTUS rows). The main place to discount me is the weight I give the Fourth Circuit decision: if the Court reads the Third, Fourth, and Fifth Circuit opinions as revealing a genuine methodological split that it wants to settle before the next interstate-enforcement fight, the response request becomes the dominant signal and the right number is closer to 0.12. Nothing I found reveals this petition's own disposition.
