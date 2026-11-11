# Evaluation — codex-baseline · scotus/73548979 · evt-petition-disposition (cert)

**Outcome.** Cert denied on 2026-11-09, after distributions for the 10/9, 10/16 and 11/6 conferences. There was no CVSG and no noted dissent or statement.

**Scores.** The prediction was `denied` at P(grant) = 0.32. `correct` = 1 and Brier = (0.32)² = **0.1024**. The harness stamps the segment base rate and skill. No votes are scored on a cert cell. It is a forward cell (snapshot 2026-10-14).

## Reasoning quality — 0.68
The rationale is careful and transparent.
- **Anchor.** The candidate computed the ≈17.2% elevated risk-set pool correctly over 2017–2024 and labelled it properly. It also explicitly declined to double-count the first relist and to use the terminal relist and CVSG cuts as forward hazards, which is exactly right. I graded against the build the candidate ran under (`statpack-at` → 886549a3ac32).
- **Split and vehicle analysis** were accurate: King is not a trademark holding, the Texas copyright case aligns with the judgment below, and the contrary position is a concurrence. The analysis also engaged the reply's answer on Penn Central.
- **Weakness.** After building a strong case that the split was soft and the vehicle complicated, the candidate nearly doubled the anchor, to 0.32. The uplift rested heavily on amici and on a USPTO speech relayed only through the petitioners' own supplemental brief, which the candidate itself discounted as advocacy. The size of that adjustment is not well supported by the analysis around it, and it cost Brier against the outcome. That is the main reason this grade sits below claude-baseline's despite the more thorough work.

## Predicted reasoning — 0.80
The document commits to a specific central path: "one further relist, followed by denial without a separate writing, in late October or November 2026." The record matches it closely. The petition was distributed for 11/6, denied on 11/9, and no writing was noted. The document also called no CVSG as the modal outcome (borne out) and no separate writing on denial as more likely (borne out). The grant-route discussion (QP 1 narrowed to trademarks) is conditional and unresolved. The 30% CVSG weighting looks generous in hindsight, but the modal call was right. This was specific and borne out on every central claim, which is not quite the top anchor, because a relist-then-deny path is a fairly common shape.

## Leakage
Mode is `forward`, and the log captured results for 95% of its calls. The external calls were:
- the petitioners' 9/21/2026 supplemental brief, a pre-snapshot filing whose URL was in the provisioned docket;
- two web searches that returned no usable content, aimed at the 2023 Financial Oversight precedent and the supplemental filing;
- CourtListener reads of the 2023 Financial Oversight opinion.

None of these targets this petition's disposition, and the candidate disclosed all of them. Graded `not_applicable`, `leakage_suspected` = false.

## Semantic grades
None; this is a cert cell.
