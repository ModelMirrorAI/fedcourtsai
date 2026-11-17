# Evaluation: codex-baseline, PLO v. Sokolow (No. 26-372), cert petition

Outcome: `denied` on the November 16, 2026 order list after a single distribution (Conference of Nov. 13); no call for a response, no relist, no CVSG, no noted dissent (`outcome.json`, docket snapshot 2026-11-16).

**Scores.** Predicted `denied` at P(grant) = 0.04: `correct` = 1, `brier_score` = 0.0016. This is a cert-stage cell; the segment base rate, basis and skill score are the harness's to stamp, and no votes are scored. `reasoning_quality` = 0.82; `predicted_reasoning_quality` = 0.8.

## Reasoning (`reasoning.md`)

**What it got right.** Called `denied` at P(grant)=0.04. The rationale is the most disciplined in the cell about what each number is: it identifies the frozen reached-band anchor, explains why the terminal-baseline rate and the own-Term row are not substitutes, treats the relist, CVSG, amicus and circuit cuts as overlapping terminal populations it will not multiply, and gives a denial-filtered corpus sample no weight. On the case, it fairly credits the petition (a real Pennoyer/Calderon/Plaut theory, large stakes) and then sets against it the absence of a square split, the panel's narrower grounds (court-initiated recall, dismissal without prejudice, the pending second action), the Fuld history, and the two waivers. Its further-distribution estimate (12%) was well judged.

**Weaknesses.** It noticed the August 2026 stay denial but gave it "little weight"; on this record that signal, together with two waivers and no amici, supported going further below the anchor than 0.04, and the outcome is consistent with that. The care taken not to over-infer leaves the final adjustment small and somewhat under-argued relative to the evidence it had assembled. Some of the text is process narration rather than analysis.

## Predicted reasoning

Central claims: denial on the list following the Nov. 13 conference without opinion, zero additional distributions as the modal path, no CVSG, and no separate writing. All held, and the document committed to them in plain future-tense terms with modest probabilities on the alternatives. Its remark that the denial would read as a narrow follow-on dispute is not checkable against a bare denial and gets no weight. The if-granted content (a narrowed QP, 85/15 plenary versus summary) is conditional and earns nothing either way. Specific and borne out, but the outcome was the expected one for this posture and the route claim is slightly less flat than the best in the cell: 0.80.

## Leakage

Mode `forward`; `influenced_prediction` = `not_applicable`, `leakage_suspected` = false. Forward cell run 2026-10-31, before the 2026-11-13 conference and 2026-11-16 denial. Log shows provisioned-input reads, statpack, one corpus query for four earlier-Term denials (retrieved_doc_date 2026-04-29, before resolution; none is this petition), CourtListener reads of the 2025 Fuld opinion, and one unobserved web search whose query targets the 2025 Fuld opinion, not this petition. No qp-topics read; reasoning treats the conference as future and discloses its retrieval.

## Big case

My read is 0.42: a very large Anti-Terrorism Act judgment against the PLO and Palestinian Authority with foreign-relations sensitivity and a novel finality question, but a party-specific sequel to Fuld that drew two waivers, no amici, and a first-conference denial with no separate writing.
