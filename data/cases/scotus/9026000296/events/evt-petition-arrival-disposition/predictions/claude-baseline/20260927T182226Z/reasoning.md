# Rationale for the numbers

## What I read

- `record/snapshots/2026-09-09.json`: a single docket entry, the September 1, 2026 filing of the petition, docketed September 8. Paid petition, OT2026, not capital. Petitioner Mike Singh Sethi, counsel Nissenbaum Law Group (Union, NJ). Respondents captioned as the Ninth Circuit et al., counsel of record D. John Sauer, Solicitor General.
- `record/context.json`: forward mode, band `baseline` under `sal-v4`, distribution_count 0, no CVSG, term 2026, `signals_observable: true`, `date` cut at 2026-09-09.
- `record/documents/questions-presented.txt` and `petition.txt` (40 pages, full text, not truncated). No brief in opposition exists yet.
- The Ninth Circuit's published order, Lnu v. Blanche, No. 24-4790 (9th Cir. June 3, 2026), retrieved via CourtListener (cluster 10869591).

## Anchor

The cell is a cert-stage arrival cell with a frozen `baseline` band under `sal-v4`, which matches the statpack's "Segment base rate by salience band (sal-v4)" table. Petitioner is a private party (a lawyer suing in his own name), so the anchor is the `baseline` column's bracketed `reached` rate pooled over the Term rows strictly before OT2026. The table renders OT2017 through OT2025; pooling those nine rows by their `n` (reached rates 4.7, 4.6, 4.6, 4.5, 5.6, 5.8, 5.9, 5.7, 3.9 percent on n of 1643, 1524, 1399, 1739, 1500, 1192, 1312, 1271, 1140) gives roughly 637 grant-family outcomes over 12,720 reached petitions, about **5.0%**. That figure counts GVRs in the grant family, so it matches the `disposition` claim's P(any grant). I did not use the relist-count cut's relist-0 row, which is a terminal-state rate and understates an arrival's future.

Other shape cuts consulted: the Ninth Circuit row of the originating-circuit cut (grant family about 3.2%, whole docket including IFP), and the CVSG-none row of the paid scored segment (grant family about 6.3%).

## Adjustments from the anchor

I moved well below the anchor, to **P(grant) = 0.012**, for these reasons.

1. **Subject matter.** This is a challenge to a court of appeals' discipline of a member of its own bar. The Court reviews such orders almost never; the petition's own best authority for plenary review, In re Snyder, is from 1985, and my CourtListener search for SCOTUS opinions engaging Ruffalo since 1986 returned nothing on point. The respondent is the court whose order is challenged, with the SG appearing for the federal side, a posture that itself signals how far this sits from the ordinary cert docket.
2. **No circuit split on either question presented.** Question 1 asserts a conflict with In re Ruffalo; Question 2 is a first-impression reading of Rule 47(b). The only nonuniformity the petition identifies, evidentiary standards for attorney discipline across circuits, is in Part III and the petition itself concedes it does "not form a perfectly aligned constitutional split." It is not the question presented.
3. **Error-correction framing and a weak vehicle.** The Ruffalo argument turns on whether the show-cause order gave notice of the candor findings. The Ninth Circuit's order states that it limited its sanctions "to the issues identified in the Order to Show Cause," notes that both lawyers waived an evidentiary hearing by not requesting one, and infers actual knowledge from circumstances under the California rules. Whether the panel exceeded its charges is a record-specific question the Court would have to resolve itself; Zauderer v. Office of Disciplinary Counsel already cabins Ruffalo to prejudicial surprise. Question 2 depends on characterizing the panel's candor holding as a new "requirement" rather than an application of Rule 3.3, a characterization the panel's text resists.
4. **Unsympathetic facts.** The petition does not contest that the briefs contained nonexistent cases and misattributed quotations produced by generative AI, in this and two other appeals. The Court is unlikely to want its first word on AI-fabricated citations to be a reversal of a sanction against the lawyer who filed them.
5. **Counsel and presentation.** Counsel is not a repeat Supreme Court advocate, and the petition has drafting slips (for example, misidentifying which side moved to submit on the briefs). This is a modest negative signal for how the petition will be read at the pool stage.

Factors pointing the other way, which keep me above the floor of what I would assign a routine sanctions petition: the Ninth Circuit's order is a published, 30-page opinion written expressly as guidance to the bar; the notice question has a genuine Supreme Court precedent behind it; and the finding that the show-cause *response* was itself a knowing false statement is the kind of sequence Ruffalo describes. Those make a short statement respecting denial imaginable, but not a grant.

## The other claims

- **relist-increment 0.96.** At arrival the count is zero. Nearly every paid petition that is not withdrawn or dismissed before conference is distributed at least once; the residual is a Rule 46 dismissal or withdrawal (the OT2025 Term row shows about 2% of resolutions as dismissals, some of them after distribution).
- **cvsg-increment 0.003.** The United States is a respondent and the SG is counsel of record, so a call for the SG's views is structurally near-impossible. I state a small nonzero number only for the residual chance of an unusual order.
- **summary-disposition-route 0.40.** Conditional on a grant. The modern-cert table's grant family is about 47% GVR (577 of 1,232), but no intervening decision exists here, so a GVR has no hook. A summary per curiam reversal of a clear due-process error is the plausible cert-order route; plenary review as in Snyder is the alternative. I put the split slightly toward plenary.
- **dissent-from-denial 0.03.** Conditional on denial. Separate writings accompany a small share of paid denials; the fair-notice angle and AI backdrop raise it a little from that base, the petitioner's conduct lowers it. No baseline is published for this claim.
- **big_case_score 0.15.** Stakes are one lawyer's six-month suspension and reciprocal discipline. A decision would matter to federal bar-discipline procedure and would draw attention because of the AI context, but it would be a narrow procedural ruling.

## Uncertainty and where to discount me

- The anchor is thin in one sense: the `baseline` class floor pools a private-petitioner population that includes strong, well-counseled petitions, and my downward adjustment rests on a qualitative judgment about attorney-discipline petitions, not on a statpack cut for that subject. I could not query the corpus by subject for SCOTUS rows (`--topic` is circuit-only), so the corpus queries I ran returned generic recent SCOTUS rows and did not inform the number.
- No brief in opposition exists; I assume the SG waives. If the Court instead calls for a response, my number would rise but stay under 5%.
- The CourtListener docket search for No. 26-296 returned no docket, so I saw no entries beyond the provisioned snapshot. This is a forward cell; I found no indication the petition has been decided.
- I have no knowledge of this case's outcome.
