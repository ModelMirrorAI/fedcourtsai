# Why P(grant) = 0.09

**Inputs used.** Snapshot `2026-08-13.json` (cut on the response-requested day). `context.json` shows band `baseline` (sal-v4), distribution_count 1, no CVSG, forward mode. Provisioned documents: `petition.txt` (62 pp., not truncated, not OCR) and `questions-presented.txt`. No response is on the record, and I did not guess what it will say.

**Anchor.** I used the sal-v4 band table's `baseline` column, bracketed `reached` rate, pooled over Terms 2017–2025 (strictly before OT2026). Those figures run 4.0–5.9%, roughly 5.2% pooled. The 2026 row (1.8%, n=169) is my own Term and still incomplete, so I left it out. The CVSG cut (none: grant family ≈ 6.4%) and the relist-0 bucket point the same way.

**Adjustment for the called-for response.** No committed table conditions on a called-for response, so this step is my judgement. A call for a response after a waiver means some chambers flagged the petition. Received wisdom puts grants among such paid petitions at around 10% at best, and most are still denied. I move up from ~5% for that reason and for these specifics:
- *Up:* The petition alleges a split: CA3/CA5/CA7 against CA4 (*Harper*, *Life Partners*) and CA10 (*Seneca-Cayuga*). Counsel is experienced. *Younger*/*Sprint* is doctrine the Court has revisited. The parallel petition from the same proceeding drew its own call for a response and a State amicus (South Carolina), which suggests real interest in the question.
- *Down:* The Fifth Circuit opinion is unpublished and short. The split cases on the other side are old (1989, 2005, 2007) and fact-bound, so they may be distinguishable rather than truly in conflict. The state proceeding is still ongoing, and the hearing examiner proposed a ruling for petitioner, which raises vehicle and ripeness doubts. The Court would take at most one of the two petitions, and the Third Circuit case is at least as good a vehicle.

**Arithmetic.** I put the companion's grant chance at about 12%. If it is granted, this petition is most likely held. The odds it ends in the grant family (a GVR if petitioners win, or a consolidated grant) are about 0.65, which gives roughly 0.08. Adding a small chance of an independent grant brings it to ≈ 0.09.

**Increments.** relist-increment 0.97: the harness masks it on this moment, but redistribution after the response is near certain. cvsg-increment 0.03: there is no federal interest. summary-disposition-route 0.6: most of my grant mass comes from a hold followed by a GVR. dissent-from-denial 0.04. order-writers are small and consistent with that figure.

**Retrieval and timing.** The companion's docket (supremecourt.gov, read 2026-10-29) is later than my snapshot. It is public forward-mode context about a different docket. It shows no disposition, only the call for a response and two extensions to 2026-11-02. I did not open this case's own live docket.

**Uncertainty.** The biggest swing factor is the companion. If the Court grants 25-1359, this petition's grant-family odds jump, and how long it stays on hold is beyond what I can see. I am also unsure whether the asserted split is real. A sharp Pennsylvania response could easily recast it as fact-bound.
