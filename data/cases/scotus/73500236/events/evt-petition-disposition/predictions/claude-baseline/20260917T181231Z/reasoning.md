# Rationale for the numbers

**P(grant) = 0.012; predicted disposition: denied.**

## What I read

- `record/snapshots/2026-09-17.json`: paid petition (docket 25-1334, Term 2025), Colorado Court of Appeals decision of June 12, 2025 (rehearing denied July 10, 2025), Colorado Supreme Court denied review January 26, 2026. Extension application 25A1202 granted to May 27, 2026; petition filed that day. Both respondents (Century at Landmark, LLC on June 15; Marin Metropolitan District on June 16) waived the right to respond. Distributed July 1, 2026 for the conference of September 28, 2026. No amici, no CVSG, one distribution.
- `record/context.json`: mode `forward`, `band: baseline` under `sal-v4`, `distribution_count: 1`, `cvsg_date: null`, `term: 2025`, `cutoff: null`, `signals_observable: true`.
- `record/documents/petition.txt` (32 pages, full text, not truncated) and `questions-presented.txt`. No brief in opposition exists; both respondents waived, so my read of the opposing side is inference, not text.
- `metrics/statpack.md`: the modern discretionary-cert base rate, the relist and CVSG cuts, the salience band table (sal-v4), the per-Term table.

## Anchor

The context band is `baseline` and the table's heading is `sal-v4`, matching `salience_version`, so the anchor is the `baseline` column's bracketed `reached` rate pooled over the Terms strictly before 2025 that the table renders (2017 through 2024). Weighting each Term's rate by its `n`, that pool is about 5.1% over roughly 11,600 weighted petitions. That is the evaluator's yardstick, and it is the rate among all paid petitions that ever passed through the weakest band, including the ones that later climbed to `elevated` or `high`.

For shape rather than anchoring: the relist-0 bucket resolves at 1.2% granted plus 0.5% GVR; the no-CVSG bucket at 4.0% granted plus 2.3% GVR; the Term-2025 est. grant rate for the whole docket is 2.6%.

## Adjustments, all downward

1. **Error-correction framing with no split.** Both questions are phrased as "whether the Colorado Court of Appeals correctly construed case law." The petition alleges no conflict among state high courts or circuits; it calls each issue one of "first impression." The Court's Rule 10 factors are almost entirely absent.
2. **Adequate-and-independent-state-ground problem the petition itself discloses.** The petition quotes the court below saying the district's claim "was based on Colorado's due process jurisprudence" (Bloom v. City of Fort Collins), not the Takings Clause. The petition's answer is that Colorado's doctrine is *really* federal takings law at its root. That is an argument for a grant only if the Court is willing to look past a state court's own characterization of its ground, which it rarely does at the cert stage. Question 2 rests on Normandy Estates, a Colorado Supreme Court case, and the federal authorities cited (Marsh v. Fulton County, Louisiana v. Wood) are 1870s and 1880s federal common-law decisions, not constitutional holdings that bind a state court. The federal question there is thin to nonexistent.
3. **Unpublished intermediate state-court decision.** The Colorado Court of Appeals opinion is not published under C.A.R. 35(e), and the Colorado Supreme Court declined review. A non-precedential decision is a poor vehicle for "clarifying special assessment law" nationally.
4. **Both respondents waived.** The absence of any brief in opposition is the respondents' own bet that the petition will not draw a call for a response; that bet is usually right for a petition of this shape. Nobody filed as amicus, despite the petition's claim that municipal borrowing costs nationwide are at stake.
5. **Fact-bound posture.** The petition's central argument, that Century bought the parcel knowing of the levy and the lack of benefit, is an application of Penn Central expectations to specific trial-court findings.
6. **Counsel and presentation.** Counsel of record is a Denver bond-counsel firm, not a repeat Supreme Court advocate; the argument section is about eleven pages. This is a modest signal but points the same way.

Nothing points up. The subject matter (municipal special-assessment finance) has real practical stakes for one segment of the Colorado bond market but no salience beyond it, and no Justice has signaled interest in the special-assessment-versus-tax question.

Starting from 5.1% and applying these, I land at roughly a quarter of the anchor: **0.012**. I would be surprised by anything above 0.03.

## Claim-by-claim

- `disposition` 0.012, equal to `probability`.
- `relist-increment` 0.12. From one distribution and no response on file, the paths to a second distribution are a call for a response (which would redistribute after the BIO), a reschedule, or a genuine relist. The paid-segment relist cut shows roughly a quarter of petitions carrying at least one extra distribution entry, but that pool is dominated by petitions with splits or government respondents that drew a response; a waived, split-less, unpublished-state-court petition sits well below it. Long Conference petitions are also more often disposed of in one pass.
- `cvsg-increment` 0.01. No federal interest at all.
- `summary-disposition-route` 0.25 (conditional on grant). Across the per-Term table, GVRs are roughly half the grant family in Terms where the label is populated, so the population baseline is near 0.5. Here there is no intervening decision of this Court to GVR against, and the plausible grant is a plenary one on a reformulated question 1. I shade well below the population share.
- `dissent-from-denial` 0.02 (conditional on denial). Dissents and statements respecting denial are rare on paid petitions generally and rarer still where the petition alleges no split and the state court invoked state doctrine.

## Big-case score: 0.15

If decided, this would matter to Colorado metropolitan-district bondholders and developers and to the roughly $30 million of bonds at issue, and a holding on the Takings-versus-due-process foundation of special-assessment law would have some doctrinal reach. It would not be a headline case.

## Uncertainty and where to discount me

- I have no brief in opposition and did not read the opinion below itself; my account of the state court's reasoning comes from the petition's own characterization and quotations, which are adversarial.
- The Long Conference produces a small number of surprise calls for response; if one issues here, the relist claim resolves true and the grant probability would move up to perhaps 0.05, still a denial forecast.
- I did not read the earlier-run prediction directories that sit beside this one in the event folder; this forecast was formed from this run's provisioned record alone.
- Corpus retrieval added nothing case-specific: the structured filters have no topical handle on special-assessment law, and the citation lookup returned no rows (see `retrieval.md`). The CourtListener search confirmed the earlier Landmark Towers litigation in this same district but did not surface the unpublished 2025 opinion or the Supreme Court docket.
