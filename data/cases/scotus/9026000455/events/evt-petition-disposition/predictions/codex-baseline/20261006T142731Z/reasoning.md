# Rationale

## Record and target

I predict denial, with **P(any grant) = 0.025**, for Leanda Chaffins v. Shannon Sharp, et al., No. 26-455. I read the provisioned event, context, and `record/snapshots/2026-10-06.json`. This is a forward cert cell with sal-v4 band `baseline`, Term 2026, zero petition distributions, and no CVSG. The snapshot is dated October 6, 2026; no live corpus freshness claim is made.

The petition was filed April 15 and docketed October 5. The intervening proceedings concern permission to file a supplemental appendix under seal. The October 5 grant of motion 26M8 is not a cert grant and is not outcome leakage. The snapshot specifies a November 4 response deadline. I retain the harness's zero distribution count: the July conference distribution was of the motion, not the petition. The event's declared distribution moment is therefore earlier in the petition's trajectory than its ordinary contract describes; this is flagged rather than silently repaired.

No document directory or document manifest was provisioned. I retrieved the exact petition and public appendix PDFs linked in the snapshot from the Supreme Court's site, without retrieving the current docket or the petition's disposition. The petition supplies substantive allegations, not adjudicated facts. The public appendix contains only a cover and the February 25, 2026 rehearing-denial order; it does not supply the January merits decision or the district court's reasons. A date-bounded CourtListener MCP search for the Eighth Circuit opinion was throttled. I made no direct CourtListener REST request and proceeded without it. I have no known or encountered disposition of this cert petition.

## Anchor and adjustments

The committed `metrics/statpack.md`, “Segment base rate by salience band (sal-v4),” matches this cell's salience version. Pooling the baseline **bracketed reached** rates for every displayed prior Term, 2017–2025, gives approximately **5.01%**, with weighted resolved denominator **12,720**. This calculation weights each displayed rate by its displayed denominator; it is approximate because the table rounds percentages. It excludes Term 2026 and does not substitute the much lower terminal-baseline rate. This is the private-petitioner risk-set anchor, not the pooled rate across caption classes.

I also read the modern discretionary-cert disposition section, the paid-segment relist and CVSG cuts, and the originating-court cut. These are descriptive population context, not independent multipliers. In particular, terminal relist buckets cannot supply the prospective probability of a new distribution from this record, and the motion distribution cannot justify a relist-based uplift. I use the prior-Term risk-set pool, not those terminal cuts, for the numerical anchor.

The petition's questions presented (PDF page 2) concern Younger abstention for constitutional violations preceding state proceedings and Rooker-Feldman treatment of independent damages claims. Its statement (PDF pages 8–10) alleges a warrantless child removal before a custody order and dismissal of the subsequent federal suit. Its reasons section invokes existing limits on both doctrines and alleges a conflict with Second and Ninth Circuit child-removal decisions (PDF pages 17–19). These are intelligible and consequential issues, which justify retaining a nontrivial grant tail.

I reduce the roughly 5% risk-set prior to 2.5% principally for vehicle and conflict uncertainty:

- The petition describes the Eighth Circuit decision as unpublished (PDF page 8), and the actual opinion is unavailable here. I cannot verify that it adopts the broad rule the petition attacks.
- The alleged split is presented through child-removal precedents and the asserted result below; the retrieved materials do not demonstrate opposing holdings on materially identical abstention and jurisdictional postures. I have not independently verified the petition's characterization of those authorities.
- Although the second question isolates damages, the petition acknowledges that the complaint also requested return of the child and discusses an opportunity to amend that request (PDF pages 13–14). Whether damages claims can be separated from custody-directed relief is a vehicle issue, not a fact I resolve in petitioner's favor.
- The asserted grounds below involve both Younger and Rooker-Feldman. Without the lower opinions, complaint, or an opposition brief, I cannot determine the relationship between those grounds, the timing of the federal and state proceedings, or whether the proposed questions dispose of the whole judgment.

The adjustment is judgmental, not an estimated subgroup rate. I do not infer adverse facts from the sealed appendix or treat the not-yet-due opposition as a concession. The absence of advanced docket signals is expected at this early posture, not independent negative evidence. The largest uncertainty is what the actual lower-court reasoning would show: a clean categorical bar to independent damages claims would warrant a higher estimate; a record-bound application or an independent obstacle would warrant less.

## Other probabilities and stakes

The 0.97 distribution-increment estimate means a first petition distribution is likely from the frozen zero baseline. The modal path is one new distribution and then denial, not repeated relisting. A small residual allows withdrawal, dismissal, or other termination before distribution. The 0.004 CVSG estimate reflects the state-official, individual-remedies posture and lack of an identified special federal institutional interest. Both are subjective prospective estimates, not lookups from the terminal statpack buckets.

The 0.40 summary-route estimate is conditional on a grant, not an unconditional 40% chance of summary relief. On that rare branch, an evident misapplication of existing jurisdictional limits could attract summary correction, while a need to clarify the distinction among remedies favors plenary review. I identify no specific intervening-decision GVR catalyst. The 0.02 separate-writing estimate is conditional on denial and forecasts aggregate existence only.

The stakes score of 0.45 reflects the broader implications of access to federal court for child-removal claims, distinct from the low probability this vehicle is selected. It does not imply that the alleged constitutional violations have been established. All facts beyond the snapshot come from the petition and its public appendix identified in `retrieval.md`; no opposition content, lower-court merits reasoning, or case outcome was available to balance the advocacy.
