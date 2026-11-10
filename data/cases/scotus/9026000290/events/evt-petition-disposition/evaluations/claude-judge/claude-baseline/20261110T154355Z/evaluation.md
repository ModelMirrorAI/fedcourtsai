# Evaluation — claude-baseline, scotus/9026000290 (*Emberton v. Superior Court of California*), cert disposition

**Stage:** cert (forward, distribution moment). **Outcome:** denied on Nov 9, 2026, after one distribution (Nov 6 conference). No CVSG, no noted dissent.

## Scores
- `predicted_disposition` denied vs. actual denied → **correct = 1**.
- P(grant) 0.004 → **Brier = 0.000016**.
- The harness computes the base rate and skill and stamps them; I leave them to the stamped segment base rate. Cert votes are not scored. The claims block is scored in code.
- No semantic set is declared, so I wrote no `semantic_grades`.

## Reasoning quality: 0.75
The rationale is concise and sound. It anchors on the pooled baseline-band reached rate (~5%). It correctly notes that the relist-0 figure describes petitions that *ended* undistributed and so understates the risk set. It then applies the right downward adjustments:
- pro se in the paid lane;
- a poor interlocutory vehicle with likely state procedural grounds;
- a "conflict" that is internal to this Court's precedent rather than a lower-court split;
- a petition that mixes RICO, § 242 and state ethics claims;
- distribution with no response.

It flags honestly that a waiver may be unrecorded. Its main deduction is depth: it read the petition only in part and leaves the finality question at "likely" without developing it. The 0.3 summary-route figure is anchored to a GVR share, which is a reasonable choice that it states openly.

## Predicted reasoning: 0.60
I treated these as central: denial at the Nov 6 conference by a plain order-list entry; no further distribution; no response called for and no CVSG; and no separate writing. All were borne out (denial on the Nov 9 order list, distribution_count 1, cvsg_date null, no noted dissent). These calls are specific but close to the default path, so they discriminate little. The conditional QP-reformulation content is unresolved.

## Leakage
Forward cell; `influenced_prediction` = not_applicable. The candidate retrieved nothing beyond the provisioned inputs and the committed statpack. There were no web, MCP or corpus lookups, nothing after the snapshot is cited, and nothing under `data/qp-topics/` was read.

## Big case
My own read is 0.04.
