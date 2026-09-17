# Rationale for the numbers

**P(grant, any form) = 0.30; predicted disposition `denied`; the grant route if it comes is `gvr` (Munsingwear).**

## What I read

Provisioned inputs: `record/snapshots/2026-09-17.json`, `record/context.json` (mode `forward`, band `elevated` under `sal-v4`, `distribution_count` 2, no CVSG, Term 2025), and all three provisioned documents — `questions-presented.txt`, `petition.txt` (20 pp.), `brief-in-opposition.txt` (15 pp.), none flagged `empty_text` or truncated. The reply brief is on the docket (5 Aug 2026) but was not provisioned, so I have not seen the petitioner's answer to the government's equitable arguments. I did not read the earlier predictions in this event's `predictions/` tree.

## The posture

A private federal prisoner (Arnold & Porter counsel) lost a §2241 saving-clause challenge to a 2003 mandatory-Guidelines career-offender sentence; the Fourth Circuit held Jones v. Hendrix forecloses the saving clause even for constitutional claims and that this raises no Suspension Clause problem (147 F.4th 452, panel divided only on reasoning). About three weeks after the mandate, petitioner's supervised release ended, mooting the case. The petition asks only for Munsingwear vacatur. The government waived, the Court called for a response, and the Solicitor General filed a full opposition with four arguments: (1) the case would not have been certworthy absent mootness; (2) Munsingwear is a civil-case practice; (3) the dismissal below was jurisdictional anyway; (4) equities — the claim was arguably moot on release from prison in June 2024, the mooting event (early termination of supervised release) came at petitioner's own request, and he could have withdrawn the appeal.

## Anchor

Cert stage, `moment: distribution`, band `elevated`, `salience_version` `sal-v4`, which matches the statpack's *Segment base rate by salience band (sal-v4)* table. Pooling the bracketed **reached** rate for `elevated` over every rendered Term strictly before OT2025 (OT2017–OT2024, weighted n = 2810) gives **17.2%**; the last five of those Terms alone give 18.1%. That is my anchor and the yardstick this cell is scored against.

One caveat about what the anchor conditions on. The band is driven by relist count, CVSG, and circuit; the `distribution_count` of 2 reads as one relist, but the first distribution (for 1 May) never reached conference because the Court called for a response beforehand. So the docket carries a zero-conference trajectory plus a **request for a response**, which the scorer does not read. The statpack notes the count is an upper bound for exactly this reason. I treat the two as roughly offsetting: the spurious relist inflates the anchor, the unpriced response request deflates it, and a called-for-response petition's grant rate is, from what I know of the Court's practice, in the same low-to-high-teens range as the anchor.

## Adjustments

Up from the anchor:
- **The Court itself flagged this petition.** A response request after a government waiver means at least one Justice wanted the SG's view before letting it go. That is the strongest observable signal on the docket.
- **The ask is cheap and the posture is textbook.** Mootness arose after the appellate judgment and before cert could be sought — the classic Munsingwear window — and the Court routinely grants such vacaturs by summary order (the corpus's modern cert population runs about 1.3% `gvr`, and the Court's recent Munsingwear orders — Beers v. Barr, Bank of America v. Miami, Gray v. Wilkie, Azar v. Garza — show it does so freely where the equities are clean).
- **The "civil cases only" argument is weak.** The Court has vacated for mootness in criminal matters before (United States v. Juvenile Male, 2011), and the Eighth Circuit dictum the SG leans on is not the Court's law.
- Elite counsel and a published, precedential opinion whose "legal consequences" are concrete for a class of prisoners.

Down from the anchor:
- **The Solicitor General opposes outright**, and the Court gives the SG's view on Munsingwear vacatur real weight; Azar v. Garza frames vacatur as equitable and case-specific, not automatic.
- **The Bancorp voluntary-action point has bite.** Petitioner's own early-termination motion moved the mooting date from June 2027 to December 2025. That is not a settlement, and the government agreed to the motion, but it is the kind of self-caused mootness the Court has treated as disfavoring vacatur. I cannot see the reply's answer to it.
- **The underlying question has drawn no appetite.** The Court has not shown interest in the post-Jones constitutional-claim question, the SG says there is no conflict, and my CourtListener searches for published circuit decisions on the point returned nothing usable (see `retrieval.md`) — so I could not confirm any percolation. Under the SG's "would have been certworthy" gloss the petition is thin.
- The Court reviews a jurisdictional dismissal, and some Justices are on record as wary of using vacatur to erase lower-court precedent.

Net: the case-specific evidence pushes moderately above the anchor because of the response request and the clean Munsingwear timing, and back down because the SG's equitable arguments are substantial and the Court generally follows the SG on vacatur. I land at **0.30**. With the modal outcome a denial, `granted` is 0 and `predicted_disposition` is `denied`; if the 30% branch fires the disposition is `gvr`, which is why `summary-disposition-route` is 0.95.

## The other claims

- `relist-increment` 0.35: from two shown distributions and zero conferences held, a further distribution happens if the Court relists to write the vacatur order or to let a Justice write on a denial. I weight it about 0.55 on the grant branch and about 0.25 on the denial branch.
- `cvsg-increment` 0.01: the SG is a party.
- `summary-disposition-route` 0.95: conditional on a grant, it is a Munsingwear GVR in the order itself; plenary review is essentially foreclosed by the petition's own ask.
- `dissent-from-denial` 0.15: banked, not scored. A statement from a Jones dissenter about the no-forum problem is plausible given a Justice's demonstrated interest, but most called-for-response denials are silent.

## Uncertainties and where to discount me

- I have not read the reply brief; if it persuasively answers the voluntary-action point, the number should be higher.
- The pseudo-relist in the band is a measurement artifact I have reasoned around rather than corrected for; the anchor may be a point or two high for this docket's true trajectory.
- My sense of the called-for-response grant rate and of the Court's deference to the SG on Munsingwear comes from general knowledge, not from a committed cut; the statpack has no response-requested cut for cert petitions.
- The CourtListener full-text searches for post-Jones circuit percolation returned zero results twice, which reads as an index or query issue rather than evidence of no percolation.
- No MCP call errored; the corpus query and the statpack were read as described. Forward mode, so no leakage concern: the petition is set for the 28 September conference and no disposition can exist as of today.
