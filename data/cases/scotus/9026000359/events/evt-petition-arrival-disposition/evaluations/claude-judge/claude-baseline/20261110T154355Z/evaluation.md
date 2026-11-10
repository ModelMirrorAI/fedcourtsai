# Evaluation — claude-baseline, evt-petition-arrival-disposition (scotus/9026000359, No. 26-359)

**Stage:** cert (arrival moment, forward). **Outcome:** denied 2026-11-09 after a single distribution (respondent waived 2026-10-09; distributed 2026-10-14 for the 11/6/2026 conference); no CVSG, no noted writing.

## Scores
- denied vs. denied → **correct = 1**.
- P(grant) 0.01 → **Brier = 0.0001**.
- Segment base rate, skill, and basis are the harness's; refer to the stamped segment base rate. No votes scored (cert stage).

## Reasoning quality — 0.88
Strong. It anchors on the pooled prior-Term `baseline` reached rate and makes explicit downward adjustments that are each grounded in the record. The QPs are not legal questions, and the string cite in Part II shows agreement, not conflict (error correction). The case is a fact-bound summary-judgment vehicle. The jurisdictional statement cites §1257(a), which I checked and confirmed in the petition. The panel below was unanimous and published, which the candidate confirmed through a legitimate pre-cutoff CourtListener lookup of the CA6 decision. It also notes the cannabis setting. The adjustments up are acknowledged and small. Limitations are candid. Minor deductions: some of its argument from advocacy signals (counsel profile, rhetorical flourishes) is heuristic, and the Sixth Circuit by-circuit figure is a mixed-class cut, which it uses only as color.

## Predicted reasoning — 0.95
Central claims: denial; the City likely waives, putting the petition on a November 2026 conference; one distribution, then denial at the first conference with no relist; no CVSG; no separate writing. Every one held, including the waiver and the November conference. The waiver is a specific, discriminating call that a competent reader could have missed (another candidate keyed its timing on the response deadline instead). The conditional GVR-route content is untested and earns nothing either way.

## Leakage
Forward; created 2026-09-27. The CourtListener retrieval was the lower-court decision (dated 2026-06-18, before the cutoff), which is legitimate forward signal. It made no query for this petition's outcome. `not_applicable`, `leakage_suspected = false`.
