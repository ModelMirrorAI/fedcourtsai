# Rationale: P(grant) = 0.07

**Anchor.** `context.json` freezes band `baseline` (sal-v4), one distribution, forward mode, cutoff 2026-08-14. The statpack's *Segment base rate by salience band (sal-v4)* gives baseline's bracketed `reached` rate. Over OT2017–OT2025 that is roughly 4–6% per Term (e.g. 4.0% n=1314 in OT2025, 5.9% n=1274 in OT2024), pooling to about 5%. OT2026's own row (1.8%, n=169) is my own Term and is incomplete, so I set it aside.

**Adjustment for the called-for response.** No committed table conditions on a response request, so this step is my judgement. A call for a response shows that at least one Justice's chambers wants the petition answered. That lifts it above the run of baseline petitions, but most such petitions are still denied. I move up only modestly, from ~5% to ~7%.

**What holds it down (from `petition.txt` and `questions-presented.txt`):**
- The decision below is an unpublished Ninth Circuit memorandum disposition.
- The QP is framed around fact-bound error correction (video evidence, comparators, harassment evidence).
- The petition concedes that petitioner "did not invoke McDonnell Douglas below." That is a vehicle problem for a question about whether the framework should apply at all.
- The Court denied *Hittle v. City of Stockton* (24-427) on this theme over Justice Thomas's dissent. The corpus row shows it denied 2025-03-10 after 5 distributions.
- A web search surfaced several other OT2026 petitions on the same *McDonnell Douglas*/Rule 56 issue (e.g. 26-80, 26-385, 26-448). If the Court wants the issue, it can pick the cleanest of them. That cuts against a plenary grant here, but it adds some hold-then-GVR probability, which is part of why I am at 0.07 rather than lower.

**What holds it up.** Justice Thomas, joined by Justice Gorsuch, has openly invited the question (*Ames*, 605 U.S. 303 (2025), concurrence). The circuit "chorus" the petition collects (*Awe*, 5th Cir. 2026, Elrod, C.J., concurring) is real. Represented counsel includes First Liberty Institute.

**Claims.**
- **relist-increment 0.97.** It is near-certain the petition is distributed again after the response. The harness masks this claim on this moment anyway.
- **cvsg-increment 0.01.**
- **summary-disposition-route 0.55** (conditional on a grant), for the hold/GVR reason above.
- **dissent-from-denial 0.20** (conditional on a denial). Thomas wrote in *Hittle*, and the call for a response may serve a writing. But he need not write on every vehicle, especially a weak one.

**Big-case score 0.3.** The issue matters, but this vehicle is narrow.

**Uncertainty.** Who called for the response is unknown. If it was a Justice inclined to grant the issue rather than to write, my number is low. I did not read the respondent's brief: it postdates my snapshot and is not provisioned. I also did not check the live docket for later entries.
