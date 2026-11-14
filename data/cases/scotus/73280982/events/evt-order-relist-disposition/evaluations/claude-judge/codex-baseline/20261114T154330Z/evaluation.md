# Evaluation: codex-baseline

**Outcome.** On 2026-11-13 the Court granted the petition, limited to the first question in the Solicitor General's reformulated wording (`actual_disposition: granted`, route plenary). This is a cert-stage cell; the segment base rate and skill are the harness's to stamp.

**Scores.** Predicted `granted-in-part` at 0.79. Brier = 0.0441. `correct` = 0 under the exact-label rule, because the outcome label is `granted` and the prediction's is `granted-in-part`. That zero is a label mismatch and not a substantive miss: the order reads "Petition GRANTED limited to the following question," which is what the candidate forecast. I have flagged the vocabulary question in `flags.json`.

**Reasoning quality: 0.85.** This is the strongest analysis of the three. It reads the distribution history correctly (three distributions, one true post-SG relist) and warns against treating the stored count as three relists. It uses the frozen anchor as the starting point and treats the CVSG, relist and amicus cuts as cross-checks that overlap, not as independent multipliers, and says plainly that the move from about 35% to 79% is judgment and not an empirical frequency. It accurately reports the SG's recommendation (grant Question 1 only, reformulated; no GVR or hold) and engages the respondents' actual objections: that the inquiries merely converge on these facts, that the reformulation creates no real controversy, and that the Item 303 theory survives regardless. It explains why the SG's express treatment of those points makes a limited grant more likely than denial or a two-question grant, which is what happened. It checks *Macquarie* itself to avoid overreading it as disposing of the Item 303 theory, and discloses which documents were truncated and that web requests returned nothing usable.

Minor weaknesses: the pooled relist rate it reports (about 20.7%) is computed loosely from rounded rates, the 0.42 probability of a further distribution was high for a first post-SG relist, and one corpus lookup was expensive and yielded nothing.

## Predicted reasoning

Grade 0.9. Central claims: a grant limited to the first question in the SG's formulation or a substantively equivalent one, declining Item 303 (borne out; the granted question is the SG's wording verbatim); modal path of a grant after Nov. 13 with no further distribution (borne out, though held at only 58%); plenary review (borne out); a bare cert order with no writing (borne out). The disposition, scope and wording calls were specific and could have gone otherwise. Slightly short of 1.0 because the no-further-distribution call was hedged close to even.

## Leakage

Forward cell, written four days before resolution. Retrieval targeted *Macquarie* and *Omnicare* only (corpus rows dated 2023 and 2013, a CourtListener read of the 2024 opinion). Two web-search rows are unobserved and were graded on their queries, which name the *Macquarie* slip opinion. Nothing sought or surfaced this petition's disposition. `not_applicable`.
