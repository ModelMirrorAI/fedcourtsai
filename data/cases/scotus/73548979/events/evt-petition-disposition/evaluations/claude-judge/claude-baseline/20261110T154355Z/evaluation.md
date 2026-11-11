# Evaluation — claude-baseline · scotus/73548979 · evt-petition-disposition (cert)

**Outcome.** Cert denied on 2026-11-09, after distributions for the 10/9, 10/16 and 11/6 conferences. There was no CVSG and no noted dissent or statement.

**Scores.** The prediction was `denied` at P(grant) = 0.22. `correct` = 1 and Brier = **0.0484**. The harness stamps the segment base rate and skill. No votes are scored on a cert cell. It is a forward cell (snapshot 2026-10-14).

## Reasoning quality — 0.75
This is a well-built rationale.
- **Anchor.** The candidate pooled the sal-v4 elevated *reached* rates over Terms 2017–2024, strictly before the case's Term, to get ≈17.2%. That is the correct risk-set figure for a frozen band. I graded it against the build the candidate ran under (`statpack-at` → 886549a3ac32), and the figure is consistent with it. The candidate also used the terminal relist cut for shape only and said so, which is correct.
- **Case-specific adjustments** were accurate and on point. On QP 2, Financial Oversight left Puerto Rico's immunity open, and here the Commonwealth itself is a party. On QP 1 there are real vehicle problems: Penn Central was disclaimed, other theories were treated as waived, and the split is soft. The candidate called the USPTO-speech supplemental brief weak, and that judgment was sound.
- **Weakness.** The candidate read the relist as possibly preparing a dissent, and that writing never came. The adjustments also netted out to a figure a little above an anchor the case-specific negatives arguably pulled down. These are minor problems; 0.22 against a denial is a good call.

## Predicted reasoning — 0.65
The document leads with a specific procedural call: denial after one or more further relists rather than a clean denial on 10/16. That was borne out exactly by the 11/6 redistribution and the 11/9 denial. The "no CVSG" call was also borne out, and the QP 2 grant-route call is conditional and unresolved. Against that, the document's account of *why* the further relist would happen leaned on a dissent-from-denial path. It put 0.35 on a separate writing and named Justice Thomas, and no writing appeared. Its 0.4 further-distribution figure also sits uneasily with the "more often than not" prose. The central disposition and route held and one secondary specific claim failed, so the grade falls between the 0.5 and 0.75 anchors.

## Leakage
Mode is `forward`. The only external call was a WebFetch of the petitioners' 9/21/2026 supplemental brief. That is a pre-snapshot party filing whose URL was in the provisioned docket, and it was disclosed in retrieval.md and the rationale. There was no query for the disposition. Graded `not_applicable`, `leakage_suspected` = false.

## Semantic grades
None; this is a cert cell.
