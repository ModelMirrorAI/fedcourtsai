# Rationale for the numbers

**P(grant) = 0.24; predicted disposition `denied`.**

## Inputs read
- Snapshot `record/snapshots/2026-09-17.json` (the file `context.json` names). Paid docket, OT2025 number 25-1187, from the New York Court of Appeals (decided Jan 13, 2026). Entries: petition Apr 13; five amicus briefs May 15–18 (Manhattan Institute + NAHB + realtor associations; Cato; Councilmember Marte; Advancing American Freedom; 44 SoHo/NoHo artists); City waiver May 19; distributed May 26 for June 11; **Response Requested June 2**; extension to Aug 3 granted; BIO Aug 3; reply Aug 17; **distributed Aug 19 for the Sept 28 conference**.
- `record/context.json`: mode `forward`, band `elevated` (sal-v4), `distribution_count` 2, no CVSG, Term 2025, `signals_observable` true.
- `record/documents/`: `questions-presented.txt`, `petition.txt` (44 pp.), `brief-in-opposition.txt` (40 pp.), all with text. I read all three in full. I also retrieved the reply brief (not provisioned) from the Court's docket; see `retrieval.md`.

## Anchor
The band table's heading is `sal-v4`, matching my context, and `elevated` is a column, so the table is my anchor. Pooling `elevated`'s bracketed `reached` figures over the Terms strictly before OT2025 that the table renders (OT2017–OT2024, eight rows) gives 484/2810 ≈ **17.2%**. OT2025's own row (13.5%, n=275) is excluded as my own Term. Cross-checks: the relist-count cut's bucket 1 (this docket's relist count under the `distribution_count − 1` rule) runs 8.2% granted + 5.1% GVR ≈ 13% grant family; the CVSG cut's `none` row is 4.0% + 2.3%.

## Adjustments
Upward, and mostly outside what the band already encodes (the band is built from distribution count, CVSG, and originating court; the response request and the amicus count are not features of it):
1. **Response requested after a waiver.** The Court's own act of attention; a minority of waived paid petitions get one and the grant rate conditional on it is well above the docket's. This is the strongest single fact on the docket.
2. **Timing relative to Sheetz II.** The Court denied No. 25-958 (the Sheetz remand petition, same Koontz "in lieu" question in a fact-bound posture where the fee had been upheld under Nollan/Dolan) on June 15, thirteen days after calling for a response here. Public information that predates my snapshot; I read it as the Court selecting this vehicle over that one, which mildly raises rather than lowers the odds here.
3. **Cert-stage support and counsel.** Five amicus briefs including national builders and realtors; Pacific Legal Foundation as counsel of record, with a strong recent record of taking takings cases to grant (Sheetz, Tyler, Cedar Point, Knick).
4. **Nature of the question.** A categorical legal holding by an influential state high court, divided 5–1–1, reversing a unanimous Appellate Division; the question was flagged as open in Sheetz's concurrences; the current Court has shown appetite for exactions cases.

Downward:
1. **Threshold alternative holding.** The BIO's lead point is real: the Court of Appeals held first that JLWQA owners never held a property interest in unrestricted residential use, so the conversion option burdens nothing they own; the QP does not name that holding. The reply answers that this is the predicate-taking inquiry the QP already poses and cites Mendenhall / Rule 14 for "fairly included." I find the reply persuasive on the doctrine but the Court is vehicle-averse, and a Justice inclined to wait could cite this. This is the largest discount.
2. **Split thinness.** A genuine but two-court split (N.C. Supreme Court vs. N.Y. Court of Appeals), padded with an unpublished California decision and district-court rulings the BIO picks apart. The Court has granted on splits this thin in takings cases, but it is a discount from the strongest cases.
3. **Voluntariness / fact-bound framing.** The state court's construction that conversion is optional is binding; the BIO uses it to make the case look fact-bound. The reply's answer (permits are always optional in exactions cases) is doctrinally sound, so I weigh this lightly.
4. **The "elevated" label overstates the docket's relist history.** The count of 2 comes from a CFR-superseded first distribution, not a relist after conference consideration; the petition has not yet been considered with full briefing. That means the band's population is a mixed one and this docket sits on its weaker side for the relist feature, while sitting on its stronger side for attention (the CFR).

Net: roughly 1.4× the pooled band anchor, landing at **0.24**. My honest range is 0.18–0.32; the residual uncertainty is how many Justices treat the threshold holding as a vehicle defect rather than as the very question.

## Claims
- `disposition` 0.24 — equals the top-level probability.
- `relist-increment` 0.35 — from two distributions shown. Long Conference grants often issue directly; denials usually issue in the first October order list. I put P(relist | grant) ≈ 0.5 and P(relist | denial) ≈ 0.3 (dissent-writing or a reschedule, which also adds a distribution entry), giving 0.24×0.5 + 0.76×0.3 ≈ 0.35.
- `cvsg-increment` 0.04 — no federal interest; the Court did not CVSG in Koontz or Sheetz.
- `summary-disposition-route` 0.06 (conditional on grant) — no intervening decision for a GVR; per curiam reversal ill-suited to a divided state high court decision with an alternative ground. The statpack's prior-Term GVR share of the grant family runs ~37–59%, but that population is dominated by GVRs after intervening decisions, which cannot happen here.
- `dissent-from-denial` 0.22 (conditional on denial) — a Thomas or Gorsuch statement is plausible given their writings on takings vehicles and the Sheetz concurrences; Sheetz II drew none.

## big_case_score 0.55
Stakes if decided are substantial for land-use law nationwide (impact fees are ubiquitous, and the question is whether they face heightened scrutiny), with a vivid fact pattern, but it is a doctrinal takings case rather than a marquee constitutional dispute.

## Where to discount me
- I have no calibrated conditional grant rate for "response requested after waiver"; the statpack carries no such cut, so that adjustment is judgment.
- Corpus `fedcourts query` returned nothing useful for this question: the citation filter is served off ~200 rows and the granted-2020s ranking is dominated by emergency applications. My priors on comparable petitions come from the statpack and general knowledge of the Court's exactions docket, not from retrieved corpus rows.
- I did not read the five amicus briefs; the reply's characterization of two of them (Marte; the artists) is what I have.
- I do not know this case's outcome; the conference has not occurred. Nothing retrieved postdates the snapshot except my check that the CourtListener docket record was last modified Aug 19, 2026 and that supremecourt.gov shows no entry after Aug 19.
