# Evaluation — gemini-baseline

**P(grant) 0.01, predicted `denied` → correct = 1, Brier = 0.0001.**

## Cell

Cert-stage cell (`event.yaml` `stage: cert`), forward. Outcome: `denied`, `actual_granted` 0, resolved 2026-10-13 after one distribution, no CVSG, no noted dissent from denial. The prediction froze `context.band` `baseline` under `sal-v4`, so the segment base rate, skill score and basis are the harness's risk-set stamp; I leave them null and refer only to "the stamped segment base rate". `vote_accuracy` omitted (cert stage). No `semantic_grades` (cert cells declare no semantic set). `claim_scores` is computed by the harness and not graded here.

## Big case (my own read): 0.12

One petitioner's coverage dispute under a 2003 Iowa group long-term-care policy. The Erie framing does not change that the question turns on Iowa insurance law and the policy text. It may matter to guaranteed-issue LTC insureds under NAIC-modeled regimes, but there is no split and no broad federal question. The Court denied it at the first conference, with the response waived and no dissent.

## Reasoning quality: 0.55

Correct but thin. The one-paragraph rationale names two anchors: the baseline-band ~5% and the ~1.7% relist-0 rate. It then gives two sound reasons to adjust down: it is a state-law insurance question in a diversity case, and the respondent waived. Both are right and point the right way. But it engages none of the petition's actual argument: the Erie/postclaims-underwriting framing, the NAIC-uniformity claim of breadth, or the alternative certification request. It also never notes that the petition concedes there is no split, or that the panel's primary ground was the policy's plain terms. It reads the Eighth Circuit opinion (per its retrieval note) but draws nothing specific from it. "Not a broader, recurring federal question" is asserted rather than shown against the petition's NAIC argument. Calling the waiver a "strong signal" overstates it somewhat, since waivers are routine on paid petitions. The adjustment from 5% to 1% is not reasoned quantitatively. The number is defensible; the analysis supporting it is generic.

## Leakage

Forward; `not_applicable`. The log (result coverage 0.0, all rows `unobserved`, so I graded them on their queries) shows a CourtListener caption search for "Denise Child" Unum and a read of opinion 11324364. Per its retrieval note, that opinion is the Eighth Circuit decision below. Those calls ran on 2026-09-27, before the 2026-10-13 denial. The lower-court opinion is pre-petition material, not this event's outcome. Nothing outcome-revealing could exist then, and the reasoning presupposes nothing.
