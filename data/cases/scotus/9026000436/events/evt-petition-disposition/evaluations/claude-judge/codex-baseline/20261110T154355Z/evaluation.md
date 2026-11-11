# Evaluation — codex-baseline

**Cell:** scotus/9026000436 (Radiall USA, Inc. v. Ramadei, No. 26-436), `evt-petition-disposition`, stage `cert`, forward. **Outcome:** denied on Nov 9, 2026, after one distribution (Oct 7, for the Nov 6 conference). Respondent had waived a response, no response was requested, there was no CVSG and no noted dissent. Two employer-side amicus briefs were filed after the predictions were made. Baseline and skill: the anchor is the stamped segment base rate (the harness pools it from the frozen `baseline` band). I quote no rate of my own. No semantic set is declared on a cert cell, and votes are not scored.

## Scores
- predicted `denied`, P(grant) = 0.07, so `correct` = 1 and Brier = 0.0049.
- reasoning_quality **0.80**.

## Reasoning
This is a careful, well-sourced analysis. It reads Appendix A (3a–5a) and identifies three independent preservation rationales. It explains why the petition's reliance on Dupree takes an extra contested step. It checks Loper Bright's statutory-stare-decisis passage in order to discount an automatic-remand theory. It is also careful not to turn terminal relist and CVSG buckets into transition probabilities. Its adjustment above the anchor for the split is defensible. It is a little less decisive than claude-baseline in pricing how close to disqualifying the invited-error holding is, so the final number sits higher than the vehicle analysis supports.

## Predicted reasoning
Grade **0.70**. Central claims: denial because of the preservation obstacles; zero additional distributions; denial on a November orders list after the Nov 6 conference; no CVSG; no separate writing. All held. The denial order gives no reason, so the stated ground is unresolved. The document commits plainly on timing and on no relist, which is more specific than claude-baseline. The content about what a grant would look like is conditional and unresolved.

## Leakage
Forward. The only external calls were general-precedent lookups of Loper Bright (two web calls unobserved, plus CourtListener text). There was no query for Radiall's disposition and no outcome material. `not_applicable`.
