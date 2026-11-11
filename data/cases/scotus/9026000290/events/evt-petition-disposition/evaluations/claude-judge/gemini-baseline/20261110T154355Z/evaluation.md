# Evaluation — gemini-baseline, scotus/9026000290 (*Emberton v. Superior Court of California*), cert disposition

**Stage:** cert (forward, distribution moment). **Outcome:** denied on Nov 9, 2026, after one distribution (Nov 6 conference). No CVSG, no noted dissent.

## Scores
- `predicted_disposition` denied vs. actual denied → **correct = 1**.
- P(grant) 0.003 → **Brier = 0.000009**.
- The harness computes the base rate and skill and stamps them; I leave them to the stamped segment base rate. Cert votes are not scored. The claims block is scored in code.
- No semantic set is declared, so I wrote no `semantic_grades`.

## Reasoning quality: 0.72
Strengths:
- It has the sharpest vehicle analysis of the three. It identifies the lack of a final state-court judgment under 28 U.S.C. § 1257(a): the case is an interlocutory writ from a demurrer sustained in part with leave to amend.
- It usefully places the case after the 2023 N.D. Cal. removal. That court rejected the Fourth Amendment theory under *Ciraolo*, dismissed the § 1983 claims under *Younger*, and remanded the rest. This is legitimate pre-decision context.
- Its base-rate anchoring is explicit and checks out arithmetically.

Deductions:
- **QP count.** It describes "three Questions Presented", including a City Attorney disqualification question. The provisioned `questions-presented.txt` contains two QPs, both on the search question. The extra topics appear in the petition's argument, not its QPs.
- **Docketing date.** It gives the docketing date as Sept 3; the docket shows the petition filed Jun 23.
- **Unsupported figure.** It asserts that pro se paid petitions are granted at "well below 0.5%" with no source.
- **Response treatment.** It treats the lapsed response deadline as a waiver "by silence", which goes slightly beyond the record.
- **Summary route.** The 0.65 conditional summary-route figure rests on a loose argument: GVRs presuppose an intervening authority, and the candidate names none.

None of these errors touches the core call.

## Predicted reasoning: 0.62
I treated these as central: denial (resting on finality); no relist or call for response, with disposition on the first order list expected **Nov 9, 2026**; no CVSG; and no separate writing. All were borne out, and naming the exact order-list date that came true is a little more specific than the other documents. The finality rationale cannot be tested against an unexplained denial. The conditional QP and GVR content is unresolved. Overall the document is specific but on near-default calls, so I put it slightly above 0.5.

## Leakage
Forward cell; `influenced_prediction` = not_applicable. The log's result capture is 0.0, so results are unobserved and I graded each call on its query. The CourtListener MCP calls targeted the 2022–23 N.D. Cal. docket and its 2023 orders, plus a caption search for published opinions. There was also one generic `fedcourts query`. None sought this petition's Supreme Court disposition, and the reasoning cites nothing after the Oct 22 snapshot. Nothing under `data/qp-topics/` was read.

## Big case
My own read is 0.04.
