# Rationale for my numbers

**P(grant) = 0.015; predicted disposition: denied.**

## Anchor

`record/context.json` freezes this cell at `band: baseline`, `salience_version: sal-v4`, `distribution_count: 1`, no CVSG, Term 2025, mode `forward`. The statpack's "Segment base rate by salience band (sal-v4)" table matches that version, so the band anchor applies. Pooling the bracketed `reached` figure for `baseline` over the Terms strictly before OT2025 that the table renders (OT2017 through OT2024, weighted by the bracketed `n`) gives about **5.1%** (a weighted average of rates running 4.5% to 5.9%, total n around 11,600). That is the risk-set grant rate for a paid private petition that has reached the baseline band, including the petitions that later climb the ladder, and it is the yardstick this cell is scored against. The petition is `Paid` (`sJsonCaseType`), so the paid segment is the right population.

## What pushed me well below the anchor

1. **State-court origin, unpublished order.** The petition comes from an unpublished Order of Affirmance of the Nevada Supreme Court, sitting en banc, affirming a Rule 12(b)(5) dismissal. The statpack's originating-court cut shows Nevada Supreme Court petitions in the modern slice at 20 resolved, all denied, and the state-court rows generally at or near 100% denied. Thin per-court cells, but the direction is consistent across every state court listed and matches the general pattern that state-court petitions are granted far less often than circuit petitions.
2. **Adequate and independent state grounds.** The brief in opposition (read in full, 22 pages) says the state courts rested on two grounds: no property interest under Nevada easement law (no easement by necessity, prescription, or implication, citing Sloat v. Turner), and a five-year statute of limitations (NRS 11.080) running from at latest 1993. The petition's answer to the limitations point is a ripeness argument (no claim accrued until the 2021 sale). Whether or not that is right, a state limitations holding is the kind of independent ground the Court routinely treats as a vehicle defect.
3. **Fact-bound and disputed premises.** The QP asserts the parcel was rendered landlocked and valueless. The BIO says the parcel abuts a public cul-de-sac (Huffaker Place) and only the northwest corner, across a drainage ditch on the Trust's own land, lost convenient access. The petition itself concedes the Trust "only used (rather than formally owned or held a recorded easement over)" the access road. The Court does not grant to resolve whether a particular corner of a Reno parcel is reachable.
4. **No genuine split.** The petition cites three state decisions (California 1943, Connecticut 2010, Colorado Court of Appeals 2001) on abutters' access rights, plus Court of Federal Claims cases. The BIO plausibly distinguishes them, and none involves a state selling land over which a neighbor had only permissive use. The petition's own candor that the Court "has not unequivocally held" the proposition it seeks confirms this is a first-impression ask on a bad record, not a split.
5. **Low signals of stakes.** Solo practitioner, no amicus briefs, three of four respondents (NDOT, Washoe County, Green Acres) waived response; only the City of Reno filed a BIO. The reply was filed and the petition was distributed for the long conference in the ordinary course.

## What kept me from going lower

The Court has been receptive to takings petitions in recent Terms (Knick, Cedar Point, Tyler, Sheetz, DeVillier), and the petition frames its ask in Tyler's anti-sidestepping language, which could catch a chambers' eye. The long conference also produces a small number of unexpected relists. That is worth a point or so above the floor I would otherwise put on a petition this weak, not more.

Net: roughly a 3.5-fold discount from the 5.1% anchor to 1.5%.

## The other claims

- **relist-increment 0.10.** The paid scored segment's relist cut shows most petitions end at zero relists; a first relist is more often a reschedule or a hold than interest. Nothing here suggests a hold, so I sit below the population's unconditional rate.
- **cvsg-increment 0.01.** No federal interest.
- **summary-disposition-route 0.40 (conditional on grant).** Plenary review of this vehicle is hard to imagine, so conditional on any grant a GVR is nearly as likely, but I know of no intervening decision to GVR in light of, which keeps this from going higher.
- **dissent-from-denial 0.03.** Aggregated existence only. Weak petition, no split, no amici.

## big_case_score = 0.12

Stakes are local: one family trust's access to one corner of one parcel. A decision could matter for how states dispose of surplus right-of-way, but as framed and on this record the significance is low.

## Inputs used

- `record/snapshots/2026-09-16.json` (the file `context.json` names; docket No. 25-1254, `sJsonCaseType: Paid`, one distribution entry).
- `record/context.json`.
- `record/documents/questions-presented.txt`, `petition.txt` (read the jurisdiction, statement, and reasons-for-granting sections; `documents.json` marks the 194-page PDF truncated, which affects the appendix, not the argument), `brief-in-opposition.txt` (read in full). No document carried `empty_text: true`.
- `metrics/statpack.md`: modern cert disposition, originating-court, relist, CVSG, and salience-band sections, and the per-Term band table.
- One `fedcourts query` corpus pull (see `retrieval.md`), used only to confirm the service was reachable; its rows were not similar enough to this dispute to move the number.

## Uncertainty and where to discount me

The biggest uncertainty is whether I am underrating the Court's appetite for takings cases. If a Justice's chambers reads the Tyler hook charitably, a relist and a statement respecting denial become more plausible than I have priced. The per-court statpack cells for state courts are small (n=20 for Nevada), so I leaned on the general state-court pattern rather than that cell alone. I did not consult the CourtListener MCP server: the snapshot is dated today and the conference is twelve days out, so no disposition could exist and I expected no information gain. Mode is `forward`, so no leakage concern arises; I have no knowledge of this petition's outcome.
