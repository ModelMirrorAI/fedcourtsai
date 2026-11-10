# Evaluation — scotus/9026000314, evt-petition-disposition (cert)

**Outcome.** The petition was denied on 2026-11-09. It was distributed once, on Oct 14, for the 11/6/2026 conference. There was no CVSG, no relist, and no noted dissent. The SG waived response on Oct 8. `actual_granted` = 0.

This is a **cert** cell. The segment base rate, the skill score and the basis are stamped by the harness from the committed statpack. I quote no rate of my own; comparisons below refer to "the stamped segment base rate". Every candidate is a **forward** prediction made from the 2026-10-15 snapshot (cutoff null, `moment: distribution`).

| Alias | P(grant) | Predicted | correct | Brier | reasoning_quality | predicted_reasoning_quality |
|---|---|---|---|---|---|---|
| codex-baseline | 0.008 | denied | 1 | 0.000064 | 0.85 | 0.75 |
| claude-baseline | 0.004 | denied | 1 | 0.000016 | 0.80 | 0.75 |
| gemini-baseline | 0.001 | denied | 1 | 0.000001 | 0.50 | 0.50 |

## codex-baseline
This is the most careful rationale. The candidate anchors on the baseline band's risk-set rate, pooled over prior Terms only. It then moves well below that anchor for concrete reasons drawn from the record:
- The actual D.C. Circuit order (App. 1a–3a) rests on two threshold grounds: timeliness, and the absence of any identified non-rule action or direct-review statute. The candidate notes that this order is narrower than the petition's characterization of it, which weakens the asserted conflict with *Norton*.
- There is no inter-circuit split.
- Rehearing en banc was denied without a vote request.
- The SG waived response, and there was no call for a response.

It also weighs a genuine counterweight. The statutory command incorporates SAE J3069, but the agency excerpt says compliance with the rule can coexist with compliance with J3069, so whether the duty is truly unperformed is contested. The analysis is sound, sourced to page cites, and well calibrated. I docked it slightly because 0.8% is a little generous for a pro se, waived-response petition with no call for response. Its handling of that factor is defensible, though.

## claude-baseline
This is a concise, accurate rationale with the same anchor and the right drivers:
- a pro se petitioner;
- an SG waiver with no call for response before the first conference, which the candidate rightly treats as close to dispositive;
- an unpublished order with an alternative ground;
- no split.

Calling the order a "Rule 36 order" is a small unverified label, but immaterial. The analysis is less sourced than codex-baseline's but correct in substance, and well calibrated.

## gemini-baseline
The candidate reached the right answer from the right factors: pro se, an unpublished untimeliness dismissal, the SG waiver, and no split. However, the rationale is a single paragraph that engages none of the record's specifics. It describes the dismissal only as "untimely", missing the alternative no-reviewable-action ground. It also asserts "fact-bound and vehicle-poor" without support. The 0.001 is defensible given the outcome, but the reasoning offers little analysis to justify going that far below the anchor.

## Predicted reasoning
Every forecast's central claims are the modal path for a waived, pro se paid petition: denial at the first conference, no relist, no CVSG, and no separate writing. All of them were borne out by the docket (one distribution; DENIED Nov 9 after the 11/6 conference) and by the outcome (`noted_dissent_from_denial` false). Each document's conditional grant content (which question, plenary versus summary) is unresolved and was neither credited nor penalized.

- **codex-baseline (0.75):** Specific and fully borne out. It names the November 6 conference and a November orders list, puts explicit small probabilities on a relist, a CVSG and a noted writing, and points out that a request for a response would not be a CVSG. The calls are what a competent reader would make here, so they are less discriminating than the 1.0 anchor requires.
- **claude-baseline (0.75):** Equally specific and borne out. It names the 11/6 conference as the only one, predicts no call for a response (correct: the docket shows none), and gives the reason a CVSG was off the table. It is graded the same as codex-baseline for the same reason.
- **gemini-baseline (0.50):** Right in direction, but generic. It commits to no conference or timing, and its three claims are the defaults.

## Leakage
All three logs record `mode: forward`, and the case was undecided when each prediction ran on 2026-10-15.
- **codex-baseline:** web searches were aimed at the Supreme Court Rules and *Norton*; none named this petition.
- **claude-baseline:** no external retrieval.
- **gemini-baseline:** one corpus query, bounded `--decided-before 2026-10-15`, that does not target this case.

No log or prose shows this case's disposition, a document dated on or after 2026-11-09, or any read of `data/qp-topics/`. All three are graded `not_applicable`, with `leakage_suspected` false.

## Big case
My read is 0.10: a narrow pro se vehicle on an administrative-law question of some general interest, denied without a noted writing.

## Other
I consulted no corpus or base-rate source, because no candidate's base-rate use needed checking against a rebuilt statpack to settle a grade. Every candidate's anchor is described qualitatively and is consistent with a roughly 4–6% baseline risk-set band. No `semantic_grades` block was written, because this is a cert cell. `vote_accuracy` is omitted, because this is not a merits stage.
