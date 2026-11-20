# Reasoning — Tedford's Tenancy, LLC v. City of New York (No. 26-110)

**P(grant) = 0.03.** Predicted disposition: denied.

## What I read
- Snapshot `2026-09-10.json`: paid petition from the N.Y. Appellate Division, First Department (leave denied by the N.Y. Court of Appeals 17 Feb 2026); both the State and City respondents waived; five amicus briefs (Realtors/NAHB, Manhattan Institute, NY Apartment Association, Advancing American Freedom, Atlantic Legal Foundation); distributed once for the 28 Sept 2026 conference; response requested 9 Sept 2026 (due 9 Oct). No response is on my record and I infer nothing about its content.
- `questions-presented.txt`, `petition.txt`, `appendix.txt` (the Appellate Division's decision). No BIO was provisioned (none existed at the cut).
- `record/context.json`: band `baseline`, `cert_anchor.rate` 0.0517, `cert_amicus_line.rate` 0.163 (arm `some`, basis `arm`, 2,315 resolved).
- `record/related/26-107.json` (Walls v. Prince George's County, relation `vided-amicus`, 3 shared briefs) and that docket's corpus row.

## Anchor and adjustments
- Anchor: the frozen baseline-band reached rate, about 5.2%. The amicus reference line (16%) I weigh lightly: the prompt itself warns the `some` arm runs high in a weak band, and here the five briefs are movement/industry amici co-ordinated across two Pacific Legal Foundation petitions (four of the five were filed VIDED on both dockets), so they say more about the campaign than about this vehicle.
- The call for a response: a low bar, one Justice's interest suffices; most such petitions are denied. On its own I would treat it, with the amicus showing, as lifting the petition modestly above the band rate (perhaps 7–9%).
- Downward, and decisive for me:
  1. **Alternative holding below.** The Appellate Division held the takings claim unripe *and*, "in any event," that the complaint failed to state either a categorical or a Penn Central taking. The questions presented reach only ripeness, so a ruling for petitioner would not change the judgment. That is a classic vehicle defect a BIO will lead with.
  2. **The split is poorly teed up.** The decision below never says whether final-decision ripeness is jurisdictional or prudential; it simply applies Williamson County's finality requirement and 74 Pinehurst. The petition's QP1 characterises the dismissal as "prudential", but the label did no visible work below, and a state court is not bound by Article III in any case, which muddies a jurisdictional-vs-prudential question arising from a state-court system.
  3. **Short state intermediate-court memorandum**, with the state high court declining review.
  4. **The Court's recent record on this subject**: it denied the New York rent-stabilization takings petitions the decision below relies on (CHIP; 74 Pinehurst) in 2023–24. QP2 (futility of the hardship process) is close to a fact-bound application of Pakdel.
  5. **The companion signal.** Walls v. Prince George's County (No. 26-107) — same counsel of record, three shared VIDED amicus briefs, same first conference, and it too drew a called-for response (2 Sept 2026) — shows in the corpus as **denied on 9 Nov 2026** after a second distribution. This is a different case's public outcome, legitimately available on a forward cell, and it was material: it shows that the response call on this pair of petitions did not translate into a grant for the sibling, and it removes the "hold for a companion grant" path. I have not read the Walls petition, so I do not know how closely its question tracks this one (it is a `vided-amicus` candidate link, not the Court's own); I therefore treat it as a meaningful but not conclusive downward push.
- Upward residue that keeps me off the floor: takings-procedure questions have real pull with several Justices (Knick, Pakdel, Tyler, Sheetz), the petition is professionally done by a repeat institutional litigant, and someone at the Court asked for a response.

Net: about 3%.

## Other claims
- `relist-increment` 0.97: the petition will almost certainly be distributed again once the response is in (the corpus row still shows one distribution as of 19 Nov 2026, so the response appears to have been extended). The harness masks this claim on this moment.
- `cvsg-increment` 0.01: no federal party or federal programme is implicated.
- `summary-disposition-route` 0.15 (conditional on a grant): if anything were granted, a plenary grant on QP1 is likelier than a GVR; no pending merits case that I know of would support a hold-and-GVR.
- `dissent-from-denial` 0.07 (conditional on denial): Justices Thomas and Gorsuch have signalled interest in rent-regulation takings claims, but the alternative holding makes this a weak vehicle to write on. `order-writers` is consistent with that.

## Where to discount me
- I did not see the response or the Walls petition; if the State's response concedes the split or the alternative holding is thinner than it reads, I am too low.
- I did not fetch the live supremecourt.gov docket; the corpus row for this case (last polled 19 Nov 2026) showed it still pending with one distribution. The corpus query for it returned no disposition, and I did not look for one.
- No degraded inputs: all three provisioned documents had text and were not truncated.
