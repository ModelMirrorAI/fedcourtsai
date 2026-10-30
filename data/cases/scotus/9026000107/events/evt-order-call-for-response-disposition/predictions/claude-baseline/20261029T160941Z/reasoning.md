# Why P(grant) = 0.13

**Inputs read.** Snapshot `2026-09-03.json` (forward mode, date cut at
2026-09-03). The QP section, the full petition, and the appendix (the Fourth
Circuit's unpublished per curiam of 23 Feb 2026, the district court's oral
ruling, and the amended complaint). No BIO exists yet: the county waived, and
the response the Court called for was not due until after the cutoff. I did
not infer what that response will say.

**Anchor.** `record/context.json` gives band `baseline` (sal-v4, matching the
statpack table's heading) and distribution_count 1. I pooled the baseline
band's bracketed `reached` rate over Terms 2017–2025 in the statpack's
"Segment base rate by salience band (sal-v4)" table. Each Term sits between
4.0% and 5.9% (n ≈ 1,200–1,750 per Term), for a pooled rate of about **5%**.

**Adjustments up.**
- **Called-for response.** No committed table conditions on it. My own
  judgement is that a call after a waiver roughly doubles to triples a paid
  petition's grant-family odds, but most such petitions are still denied.
- **Amicus support.** Six amicus filings on the docket (NAR et al., NY
  Apartment Ass'n, Manhattan Institute, California Rental Housing Ass'n,
  Advancing American Freedom, Atlantic Legal Foundation; some entries are marked
  VIDED). That puts the petition in the statpack's `2+` amicus bucket (n = 1,449
  resolved, grant family about 23%). The count is a stakes proxy, it overlaps
  heavily with the relist signal, and it is measured at disposition, so I take
  only part of it.
- **Counsel and topic.** Pacific Legal Foundation is a repeat takings litigant,
  and the Court has repeatedly taken takings-ripeness cases (Knick, Pakdel,
  Sheetz). The petition pleads two splits.

**Adjustments down.**
- **Unpublished per curiam.** The Fourth Circuit's opinion is not
  precedential and is short. It reads as a fact-bound application of the
  finality requirement: the owner never sought the category amendment the
  agency letter described. That is a poor vehicle for a clean
  legislative-exhaustion rule.
- **QP 2 likely does not affect the outcome.** The dismissal was under Rule
  12(b)(6) either way, and the panel noted that neither party challenged that
  framing.
- **The splits are counted generously.** Several cited state decisions may be
  distinguishable.

**Net.** About 13% for the grant family, including a meaningful share of
summary vacatur in light of Pakdel. The summary-route conditional is 0.35
because Pakdel was itself a summary per curiam on near-identical finality
over-demands. Dissent-from-denial is 0.12, about twice a typical denial,
because of the takings subject and Justice Thomas's and Justice Gorsuch's
interest. Relist-increment is 0.97 (masked by the harness on this moment).
CVSG-increment is 0.03.

**Where to discount me.** The adjustment for the called-for response is my
own judgement, not a published rate. I have not seen the county's response,
which could expose vehicle problems (the parallel state proceedings listed in
the petition's related-cases statement) or concede the split. Corpus retrieval
added nothing (see `retrieval.md`). I did no web or CourtListener retrieval.
