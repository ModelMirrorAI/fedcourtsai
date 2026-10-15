# Evaluation — claude-baseline

**Cell.** scotus/9026000006 (Merritt v. Texas Farm Bureau), `evt-petition-disposition`, stage `cert`. Outcome: `denied` on 2026-10-13, after a single distribution for the October 9, 2026 conference, with no noted dissent (`actual_granted` 0).

**Base rate.** The scored prediction froze a band (`baseline`, `sal-v4`), so the segment base rate, its basis and the Brier skill score are the harness's risk-set anchor, filled in by `stamp-cell`. I leave them null here and quote no rate of my own. Compare against the stamped segment base rate.

**Leakage.** Forward cell: the prediction is dated 2026-10-04, before the conference and the denial. I checked the log for this case's own disposition showing up as already decided and found none (details below).

**Score.** Predicted `denied`, P(grant) = 0.007. Correct (1). Brier = 0.007² = 0.000049.

**Reasoning quality: 0.85.** This is the most specific vehicle analysis of the three. It does these things well:

- It anchors on the pooled baseline reached rate (~5.0%, n ≈ 12,720), and it explicitly treats the relist-0 terminal figure as shape only.
- It identifies the missing conflict and cites the BIO's survey of nine circuits, which the petition never disputes.
- It catches that the unchallenged "deliberately prevents the employer from acquiring knowledge" instruction independently sustains the verdict. That is the decisive vehicle point, and the other candidates do not isolate it.
- It covers the waiver dispute and the posture: a unanimous published panel affirming a jury verdict, with en banc rehearing denied.
- It names what keeps the number above zero, namely the clean textual "suffer or permit" argument.

It also states its retrieval limits honestly: two searches were throttled, and it says which points those searches left unverified. Two inputs are weaker than the rest. The petitioner-profile and counsel points carry little evidential weight, and using them invites anchoring on impressions. And going to roughly one-seventh of the band rate leans confident. The outcome bears that out, but it would cost more than the other candidates on a surprise grant.

**Leakage.** One CourtListener search returned the 2026-02-06 opinion below, which predates the resolution and is legitimate forward context. Two further searches failed with HTTP 429. Two corpus queries returned unrelated resolved rows that the candidate did not use. No `retrieved_doc_date` falls on or after 2026-10-13. Grade: `not_applicable`, not suspected.
