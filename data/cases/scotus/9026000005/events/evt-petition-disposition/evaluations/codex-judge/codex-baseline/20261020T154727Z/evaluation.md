# Evaluation: codex-baseline

## Outcome and mechanical scores

The cert-stage petition was denied on October 19, 2026, with `actual_granted = 0`. codex-baseline predicted `denied`, so `correct = 1`. Its grant probability was 0.12 and its Brier score is `(0.12 - 0)^2 = 0.0144`. The denial does not supply a merits holding or identify the Justices' reasons.

The prediction froze an elevated sal-v4 band for Term 2026. The stamped segment base rate, skill score, and baseline provenance belong to the harness and remain null here. I calculate no competing rate. Cert votes are unscored, no semantic set is declared, and quantitative claim scoring is left entirely to the harness.

## Reasoning quality: 0.92

This is a careful, well-qualified analysis of the information available before disposition. It distinguishes the present cert petition from earlier proceedings, uses the frozen band rather than reclassifying the case, and explains why two distribution entries do not necessarily mean a completed substantive conference followed by a relist. The response request falls between the two distributions, which supports the rescheduling caution.

The rationale engages both questions presented: the NLRB's separation of prosecution from adjudication and the proposed severance of executive functions rather than removal protection. It then explains why the intervening decision described in the opposition reinforces the lower court's result and why the related Harris denial reduces the need for another case. The provided opposition supports those descriptions. Importantly, the analysis attributes its account to an advocate rather than asserting that it independently read an opinion; it also explains that the companion denial is not a merits precedent.

The treatment of the binary target is particularly clear: a summary affirmance after a grant would count as a grant even though the petitioner loses substantively. The rationale separates terminal relist descriptions from forward increment hazards and identifies both missing petitioner-side follow-up and unverified opinion scope as sources of uncertainty.

The remaining weaknesses are that the numerical adjustment is judgmental rather than derived, and that a sizeable part of its grant-side allocation is a GVR despite its own explanation that the intervening precedent favors the judgment below. Those are limits on the analysis, not retrospective penalties for probabilities assigned to paths that did not occur. This grade covers `reasoning.md` alone; the forecast document and structured claims are not graded through it.

## Leakage assessment

Both context and retrieval log identify forward mode. All 27 calls occurred September 30, before the October 19 resolution. Result-capture coverage is 25/27: calls 13 and 14 are unobserved general-rules web requests, one for Rule 10's compelling-reasons language and one for the official rules PDF. Their absent results cannot independently substantiate the candidate's report that they returned no usable content. The queries themselves are generic and do not seek this petition's disposition.

The remaining logged reads concern provisioned inputs, committed statistical material, schemas, and operational checks. Related-case developments appear in the provisioned opposition and predate this forecast; they are legitimate forward evidence. No logged query, recorded document date, or supplied prose shows the target denial being known. Accordingly, `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`, with the two uncaptured results expressly acknowledged rather than treated as proven empty.

## Stakes

My independent case-level significance read is 0.80, reflecting the national reach of NLRB adjudication and the separation-of-powers question. The intervening precedent described in the filings reduces the marginal novelty of this follow-on petition, and denial announces no new merits rule. This is a stakes assessment, not a grant-likelihood assessment.
