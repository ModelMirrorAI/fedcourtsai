# Reasoning — Nexstar Media Inc. v. NLRB, No. 26-435 (arrival moment, forward mode)

**P(grant) = 0.03. Predicted disposition: denied.**

## Inputs read

- `record/snapshots/2026-10-02.json` (the snapshot `context.json` names): a one-entry docket. Petition filed Sep 28 2026, docketed Oct 1 2026, response due Nov 2 2026; paid case; Second Circuit No. 24-2818 decided June 30 2026.
- `record/context.json`: mode `forward`, band `baseline` under `sal-v4`, `distribution_count` 0, no CVSG, Term 2026, `cut_kind` `date`, cutoff 2026-10-02.
- `record/documents/questions-presented.txt` and `petition.txt` (61 pages, not truncated, text extracted). No brief in opposition exists yet; `documents.json` lists only the petition and its QP cut.
- `metrics/statpack.md`: the sal-v4 segment base-rate table, the relist/CVSG cuts, and the originating-circuit cut.

## Anchor

The petitioner is a private corporation (Nexstar Media) and the respondent is a federal agency. Under the salience scorer's caption rule the petitioner's class is `private`, so the anchor is the `baseline` band's bracketed `reached` rate, which the frozen `band: baseline` in `context.json` confirms. The table heading is `sal-v4`, matching `salience_version`, so the table is a valid anchor for this band.

Pooling the nine Term rows strictly before 2026 that the table renders (OT2017 through OT2025, n = 12,720 weighted petitions that reached `baseline`) gives a pooled grant-family rate of **5.0%**. This is the private-class arrival population's own rate, which is exactly this cell's situation. I did not use the relist-0 cut (1.2% granted), which is the rate among petitions that ended undistributed and understates an arrival's prospects; nor the originating-circuit cut (CA2: granted 2.6%, gvr 2.3%), which is over the whole modern cert docket including IFP filings.

## Adjustments from 5% to 3%

Down, and substantially, because this petition is weaker than the typical paid private petition reaching the baseline band:

1. **The posture is substantial-evidence review of fact findings, not legal deference.** The summary order (petition App. 1a-13a) states "We review the NLRB's legal conclusions de novo," treats supervisory status under Section 2(11) as a question of fact per Second Circuit precedent, and resolves the producers' status by holding that substantial evidence supports the Board's findings on assignment and responsible direction. The one sentence the petition builds on ("Legal conclusions based upon the Board's expertise should receive ... considerable deference," quoting a 2012 Second Circuit case) is not applied to anything dispositive. The Solicitor General's opposition, if one is called for, will say so, and the Court routinely declines to review fact-bound substantial-evidence losses.
2. **The circuit split is not one.** Multimedia KSDK (8th Cir. 2002, en banc) held that the producers at one St. Louis station were supervisors on that record. It announced no legal rule that television producers are supervisors, and the Second Circuit panel reasonably called it "neither binding nor pertinent." A record-specific divergence in outcomes under the same Kentucky River / Oakwood framework is not a conflict the Court takes.
3. **The intra-circuit inconsistency has already been resolved.** The petition's strongest point is that the Second Circuit, in Siren Retail Corp. v. NLRB (Sept. 2, 2026), disclaimed deference to the Board's legal conclusions two months after this summary order. CourtListener confirms that decision exists and is published. But that cuts against review: the circuit is now aligned with the Fifth, Sixth, Tenth, and D.C. Circuits, so there is no live inter- or intra-circuit disagreement for the Court to settle.
4. **Unpublished, non-precedential summary order.** The Court treats these as poor vehicles, and a GVR of an unpublished order that already recites de novo review would accomplish little.
5. **Petition quality.** The petition is 17 pages with a miscited case name throughout ("KDSK"), internal date errors in citations, and a conclusion that describes the Second Circuit as having applied an "abuse of discretion standard" to the supervisory question, which it did not (that standard governed the election-objection issue). Counsel is a management-side labor firm rather than a Supreme Court practice. None of this is dispositive, but it signals a petition unlikely to draw a pool memo recommending a response, let alone a grant.

Up, slightly, and why I stop at 3% rather than lower:

1. **The GVR ask has a precedent in form.** The Court GVR'd Hospital Menonita de Guayama v. NLRB in light of Loper Bright, and the petition expressly asks for the same. A Justice who believes lower courts are still deferring to the Board could see the "considerable deference" sentence as worth a GVR. I give this real but small weight because that GVR was for a decision issued before Loper Bright, while this one postdates it by two years and recites the right standard.
2. **Loper Bright policing is a live interest for this Court,** and the respondent is a federal agency, so a response (if called for) comes from the Solicitor General and is read carefully.

The net is a petition a good deal below its class average: roughly 0.03, of which most of the mass is a GVR rather than plenary review.

## Claims

- `disposition` 0.03, equal to `probability`.
- `relist-increment` 0.97: from the zero-distribution state, this is P(at least one distribution). Nearly every docketed paid petition that is not withdrawn or dismissed before conference is distributed once; I see no settlement or withdrawal path here.
- `cvsg-increment` 0.01: the United States (NLRB) is the respondent, so the Solicitor General is a party and is not invited.
- `summary-disposition-route` 0.75, conditional on a grant: a Loper Bright GVR is the petition's own primary ask and the shape a grant would most plausibly take; plenary review of a deference question on this record is the less likely branch.
- `dissent-from-denial` 0.04, conditional on denial: low-visibility unpublished-order petition; no amicus interest visible; the circuit has already self-corrected.

## Big-case score

0.15. The general question (post-Loper Bright review of NLRB legal conclusions) has some administrative-law salience, but this case is a one-station bargaining-unit dispute resolved by an unpublished order, and the circuits already agree on the answer. Low stakes if decided, and lower still as a GVR.

## Uncertainty and where to discount me

- No brief in opposition exists yet; my read of the government's position is inference from the summary order's own text.
- I did not read the Siren Retail opinion body; I confirmed its existence, date, and published status via CourtListener and otherwise relied on the petition's quotation of it.
- The CourtListener docket index returned no SCOTUS NLRB dockets for 2024–2026, so I could not check how the Court disposed of comparable post-Loper Bright NLRB petitions in OT2024 and OT2025 beyond the Hospital Menonita GVR the petition itself cites.
- The corpus `fedcourts query` run returned mostly emergency applications in its top ranks and no cert petition comparable to this one, so the anchor rests on the statpack alone.
- The sal-v4 baseline `reached` rate is a grant-family rate (grants plus GVRs); if the evaluator's scoring axis treats GVRs as grants, as the prompt says it does, my 0.03 is on the same axis.
