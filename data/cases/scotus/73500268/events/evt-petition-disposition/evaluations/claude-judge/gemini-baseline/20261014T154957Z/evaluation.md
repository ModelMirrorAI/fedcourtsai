# Evaluation — gemini-baseline, scotus/73500268 evt-petition-disposition

**Outcome:** GVR (`actual_disposition` gvr, `actual_granted` 1), resolved 2026-10-13, at the first conference after full briefing; distribution count stayed at 2.

**Prediction:** `gvr`, P(grant) 0.92. Correct label; Brier (0.92 − 1)² = 0.0064. This is a cert cell and the prediction froze a band (`elevated`, sal-v4), so the segment base rate, skill and basis come from the harness stamp, and `correct` / `brier_score` are stamped over. The values here are my independent read of those fields.

**Reasoning quality 0.68.** The core argument is correct and it was the decisive one. The Fifth Circuit applied the two-factor judicial-estoppel test that *Keathley* rejected. The petition asks for hold-and-GVR, and the Court's usual practice is to remand so the lower court can apply the corrected standard. The note that the response in opposition argues affirmance under the totality standard is accurate. But the document is thin:
- It never engages that argument on the merits. The opposition's case rests on facts specific to this record (the debtor knew the claims' value, scheduled the Royal American claim at $0, and amended only after Hartford challenged the omission). That case is the main route to a denial, and the reasoning dismisses it without analysis.
- It cites no part of the decision below to show the repudiated test was actually applied.
- It quotes the band anchor only loosely ("around 17-18%") and never shows the pooling.
- It does not justify 0.92 over a more hedged figure.

The number turned out well calibrated, but the written support is shallower than the confidence it states.

**Leakage:** forward cell with no outcome material. The log captured none of the call results (coverage 0.0), so I graded the calls on their queries. They target the lead case *Keathley*, not this docket. Graded `not_applicable`.

**Semantic grades:** none. This is a cert cell and no semantic set is declared.
