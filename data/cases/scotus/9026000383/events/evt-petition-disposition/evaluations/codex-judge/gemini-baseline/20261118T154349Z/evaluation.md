# Evaluation: gemini-baseline

This is a cert-stage evaluation of Scroggins v. City of Shreveport, No. 26-383. The prediction named denial with P(grant)=0.002; outcome.json records denial on November 16, 2026 and actual_granted=0. Therefore correct=1 and brier_score=(0.002-0)^2=0.000004.

## Rationale

The rationale supports a very low grant probability with concrete record evidence: the response waiver, lack of a demonstrated split, unpublished Fifth Circuit affirmance, and the district court's separate pretext holding (appendix, App. 1 and App. 17 n.1–18). Its discussion of the temporary light-duty assignment and due-process abandonment is also supported (App. 5–6 and App. 21). These are certworthiness and vehicle considerations; the eventual denial does not establish that the lower courts were substantively correct.

The limitations are methodological and legal. Terminal-band and zero-relist frequencies describe selected end states; treating them as a second starting point for a still-pending petition needs more caution. The rationale also calls the alternative pretext holding effectively fatal without engaging the petition's express Rule 56 challenge to that holding (petition, printed pp. 16–18). The separate earlier petition's denial supplies, at most, a weak analogy. The exact downward adjustment remains judgmental. These limitations, rather than the forecast document or structured claims, set reasoning_quality at 0.86.

For the base-rate discussion I checked the candidate's original statpack, recovered by statpack-at from build 648fc43559f5480348a438523a81df100b5c7301, digest sha256:063aea1961d5833e02e3aa0254477260a34f98f23a2751a1620aaf7c8db03726, rather than judging its figures against the refreshed committed pack. The cited historical table entries agree with that recovered build. The scored comparison uses the stamped segment base rate; the harness alone supplies the baseline and skill fields. No additional baseline is calculated here.

## Predicted reasoning

The central forecast was a November 16 denial after the November 13 conference, without a requested response, another distribution, or a CVSG. Each procedural commitment matches the final snapshot and outcome. This supplies substantially more discriminating content than denial alone, supporting 0.95.

The outcome expressly records no noted dissent from denial. The broader forecast of no statement respecting denial cannot be fully checked because no order text or separate-writing collection is staged; that part is unresolved. The conditional selection of QP 1 and preference for plenary review were never tested by the denial and receive neither credit nor penalty. The Court gave no substantive reason that could establish the forecast's legal explanation.

## Leakage

All 36 logged calls are outcome_only, with captured-result coverage 0.0. Their null dates and digests do not establish empty results. Queries concern provisioned inputs, historical authorities, general priors, and a separate earlier petition (26-80); a caption search is unbounded but ran before this petition resolved. Neither the queries nor the prose shows this petition's disposition. The disclosed earlier petition's denial is legitimate forward information. Assessed on queries and prose: retrieved_outcome_material=false; influence=not_applicable.

The prediction's frozen context is forward, cutoff=null, snapshot_date=2026-10-31. Its own docket's waiver and distribution were legitimate provisioned inputs. The evaluator's November 16 snapshot is used to check the result, not substituted for the candidate's information boundary.

## Stakes and scope

My case-significance assessment is 0.06: a narrow individual employment dispute, an unpublished affirmance, and no demonstrated conflict or resulting national rule. This assessment is independent of the candidates' stakes numbers. Cert votes are not scored. No semantic grades are declared at this stage, and the quantitative claims block is left entirely to the harness. The staged record contains no Supreme Court opinion or separate-writing collection; no substitute text was fetched.
