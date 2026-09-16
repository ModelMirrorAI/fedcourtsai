# Rationale for the numbers

**P(grant) = 0.025; predicted disposition: denied.**

## Inputs read

- Snapshot `record/snapshots/2026-09-16.json` (the file `context.json` names). Paid petition, docketed May 12, 2026; response due June 11, 2026; distributed June 24, 2026 for the Conference of September 28, 2026. Two docket entries in total; no brief in opposition, no waiver, no amicus.
- `record/context.json`: mode `forward`, band `baseline` under `sal-v4`, distribution count 1, no CVSG, Term 2025.
- `record/documents/petition.txt` (44 pages, full text) and `questions-presented.txt`. No BIO was provisioned because none exists on the docket.
- `metrics/statpack.md`: the modern-cert disposition section, the relist and CVSG cuts, and the sal-v4 segment table.

## Anchor

The context's band is `baseline` and the segment table's heading is `sal-v4`, matching `salience_version`, so the table is a valid anchor. The petitioner is a private party (a state criminal defendant) and the respondent is a State, so the caption class is private and `baseline` is its floor. Pooling the bracketed `reached` figures over Terms strictly before OT2025 (OT2017 through OT2024, all eight rendered prior rows, n = 11,580 weighted) gives a pooled reached grant-family rate of about 5.1%. OT2025's own row (3.9%, n = 1,140) is excluded as this case's own Term. So the yardstick is roughly 4 to 5%.

The relist cut says a paid scored petition ending at zero relists grants about 1.2% (plus 0.5% GVR); the CVSG-none bucket runs 4.0% granted plus 2.3% GVR. Those are terminal buckets, read for shape only.

## Adjustments down from the anchor

1. **No opposition on the docket.** The Court does not grant an unopposed petition without first calling for a response. A grant therefore requires two sequential events: a response request and then a grant after the response. Petitions distributed with no response are a lower-grant slice of the baseline population.
2. **The court below is a state intermediate appellate court**, and the Pennsylvania Supreme Court declined review. The Court prefers a state high court or federal court of appeals as the last word; a Superior Court panel opinion is a weak vehicle even though it is published (342 A.3d 742, 2025 PA Super 159).
3. **QP 1 is fact-bound.** The particularity question turns on a 2000 John Doe complaint listing six RFLP loci without an attached profile or random-match statistics. The petition's own survey (Belt, Police against Robinson, Boughton, Burdick, Carlson) shows the courts applying one rule and reaching different results on what the documents attached, which is a fact-pattern divergence rather than a doctrinal split. The trial court also granted the suppression motion in part, and the petition does not clear away whether alternative grounds (good faith, the later 2021 identification and arrest warrant) independently sustain the conviction.
4. **QP 2's split claim is thin.** The petition pits United States v. Davis (4th Cir. 2012) against Raynor v. State (Md.) on whether profiling is a separate search. The Court has previously declined to take the abandoned-DNA question when presented from Maryland, and no federal circuit has held the profiling of abandoned DNA to require a warrant. QP 2 as written is also truncated mid-sentence, a drafting flaw that signals the petition is not from a Supreme Court specialist shop.
5. **Unsympathetic posture.** A 1995 rape solved through a CODIS profile and genetic genealogy, with a stipulated bench trial conviction, is exactly the record on which the Court has historically let novel DNA questions percolate rather than intervene.
6. **No amici, no CVSG, one distribution**, and counsel is a regional firm rather than a repeat Supreme Court advocate.

## Adjustments up

- The shed-DNA and genetic-genealogy question is genuinely open at this Court, technologically salient after Carpenter and Maryland v. King, and recurring nationwide. It is the kind of issue that could draw a response request from one chambers, which is why my relist-increment number (0.20) is well above the share of long-conference petitions that are simply relisted.

Net: I move from about 5% to 2.5%. Roughly, P(response requested) about 0.13, P(grant | response requested and then considered) about 0.15, plus a small residual for other paths, gives about 0.02 to 0.03.

## The other claims

- `relist-increment` 0.20: dominated by the chance of a call for a response (which adds a distribution), plus a small chance of a reschedule or a relist off the long conference.
- `cvsg-increment` 0.01: state criminal case, no federal party; the paid-segment CVSG rate is about 1.2% and this case is below it.
- `summary-disposition-route` 0.08 (conditional on grant): no intervening decision to GVR against; summary reversal of a published state decision on an open question is implausible.
- `dissent-from-denial` 0.06 (conditional on denial): a statement respecting denial from a Justice attentive to digital-era Fourth Amendment questions is possible but not expected.
- `big_case_score` 0.55: if decided, the warrant question for shed-DNA profiling would be a major Fourth Amendment ruling affecting cold-case practice everywhere; the score reflects stakes if decided, not grant odds.

## Uncertainty and where to discount me

- I could not read the Superior Court opinion itself (CourtListener holds no copy), so my read of the decision below is through the petition's characterization; a BIO does not exist to correct it.
- Whether the Commonwealth waived or simply did not respond is not visible on the snapshot. If a waiver was filed and the docket simply omits it, nothing in my analysis changes; if the Court has already requested a response, my relist number is too low and my grant number somewhat too low.
- The corpus `fedcourts query` calls returned recent stay applications and merits-track grants rather than comparable state-court Fourth Amendment cert petitions, so the retrieved priors informed nothing beyond confirming the low modern grant rate; the anchor rests on the statpack alone.
- No outcome for this case was encountered. CourtListener's docket record showed no entries and a last-modified date of June 24, 2026, consistent with the snapshot.
