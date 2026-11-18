# Reasoning — No. 26-646, Williams et ux. v. Superior Court of California, Los Angeles County

**P(grant) = 0.006; predicted disposition: denied.**

## What I had

- Snapshot `2026-11-18.json` (forward mode, arrival moment, cutoff 2026-11-18). It shows a single docket entry: petition filed Nov 9 2026, docketed Nov 17 2026, response due Dec 17 2026. Paid case, not capital. Lower court: Court of Appeal of California, Second Appellate District (B356638), decision Aug 21 2026; the date listed as the discretionary-court decision (presumably the California Supreme Court's denial of review) is Oct 21 2026.
- No `record/documents/` directory was provisioned and `same-question.json` has `petitions: null`, so I have no petition text, no questions presented, and no decision below. The docket is not marked paper-only, so this just means nothing was fetched. Everything below is inferred from the docket skeleton and base rates, not from the petition's argument.
- `context.json`: band `baseline` (sal-v8), `distribution_count` 0, no CVSG, `cert_anchor.rate` 0.0517, `cert_amicus_line.rate` 0.0268 (arm `none`).

## Anchor

The arrival-moment anchor for a private petitioner is the `baseline` band's bracketed `reached` rate, pooled over prior Terms: the frozen `cert_anchor.rate` is about 5.2% (statpack Term rows 2017–2025 run 4.2%–6.0% reached). The no-amicus reference line is about 2.7%.

## Adjustments (all downward)

1. **Self-represented petitioners.** The only petitioner-side attorney entry is the lead petitioner himself, with contact details withheld by the scrub (which is applied to self-represented filers). Paid pro se petitions are granted at a small fraction of the paid-segment rate; the baseline band's grants are concentrated among petitions with experienced Supreme Court counsel.
2. **Posture.** The respondent is the Superior Court, which is the caption form of a California writ proceeding (mandate/prohibition) in the Court of Appeal. Such petitions are usually denied summarily below, leaving an unreasoned, typically unpublished order — a poor vehicle with no developed federal question and usually an interlocutory or state-law-bound dispute.
3. **Originating court.** The statpack's originating-court cut for the California Court of Appeal, Second District shows 311 resolved: denied 93.6%, dismissed 3.9%, GVR 2.3%, granted 0.3%. The GVRs there are, to my understanding, mostly criminal cases held for intervening decisions, which this civil-looking writ proceeding does not resemble. That cut includes IFP cases, so it is a cross-check rather than the anchor.
4. **No companion or same-question signal.** No Vide links, no same-question list, no amicus.

Combining these, I put the grant family (grant + GVR + summary reversal) at roughly 0.5–1%, and commit to 0.006. That is about a ninth of the scored anchor; I think the gap is justified because the anchor pools counselled business and institutional petitions with pro se ones.

## Other claims

- `relist-increment` 0.96: the snapshot shows zero distributions, so the claim is whether the petition is ever distributed for conference. Nearly every paid petition is, barring a Rule 46 dismissal, or a defect that stalls the case. I leave ~4% for those.
- `cvsg-increment` 0.002: no federal interest visible.
- `summary-disposition-route` 0.6 (conditional on a grant): if this petition were somehow granted, a GVR in light of some intervening decision is likelier than plenary review of a pro se state writ case.
- `dissent-from-denial` 0.004 and `order-writers` at 0.001–0.002 per Justice: separate writings on denials of this kind are very rare.

## Where to discount me

I did not see the petition. If it presents a genuine, well-framed federal question (say a due-process or takings claim tied to a pending granted case), my number is too low, though the pro se posture would still keep it under the anchor. The inference that the petitioners are self-represented rests on the snapshot's attorney field and the contact scrub, not on a filing.

## Retrieval

One corpus query (granted SCOTUS priors, 2020s) to satisfy the query step; it returned counselled, institutional-litigant grants (e.g. a securities case with Supreme Court specialist counsel on both sides), which supports the contrast drawn above but did not move the number. CourtListener MCP and web search were not used: with no petition text there was no specific question to research, and the state writ docket is unlikely to be covered.

`big_case_score` 0.03: nothing on the docket suggests significance beyond the parties.
