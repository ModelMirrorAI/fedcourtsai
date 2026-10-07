# Evaluation of gemini-baseline — Patterson v. Michigan, No. 25-1263 (evt-petition-disposition)

**Stage:** cert (event.yaml `stage: cert`, `moment: distribution`). **Outcome:** petition denied on 2026-10-05 after a single distribution for the 2026-09-28 conference; no CVSG, no noted dissent. **Mode:** forward.

## Scores

| Field | Value | Basis |
| --- | --- | --- |
| correct | 1 | `predicted_disposition` denied = `actual_disposition` denied |
| brier_score | 0.0001 | (0.01 − 0)² |
| segment_base_rate | 0.0512 | baseline band, sal-v4, risk-set |
| base_rate_basis | risk_set | prediction froze `band: baseline` with `salience_version: sal-v4`; the statpack table heading is sal-v4 |
| brier_skill_score | 0.9619 | 1 − 0.0001 / 0.0512² |
| reasoning_quality | 0.55 | see below |

The base rate pools the bracketed `reached` baseline figures over the rendered Terms strictly before Term 2025 (2017–2024; the table renders every Term the pack holds, so no window divergence): 593 / 11,580 = 0.05121, recorded as 0.0512. `vote_accuracy` is omitted on a cert cell.

## What the prediction got right

Right disposition, a low number, and the correct anchor: it names the baseline band's prior-Term reached rate of about 5% and the relist-0 bucket as the shaping cut, and it identifies the two features that matter most on the face of the petition, a fact-bound question and no alleged conflict. The absence of a brief in opposition is read correctly as a signal pointing toward denial. The forecast is sound as far as it goes.

## Where it is weaker

The rationale is a single paragraph and omits the petition's most serious vehicle defect: the case is interlocutory, an appeal from a bindover after a preliminary examination that Michigan's appellate courts declined to hear, so there is no final judgment under § 1257. Both other candidates treat that as near-dispositive; this one does not mention it. Two smaller points. The 1.2% relist-0 figure is the `granted` label alone; the grant family in that bucket is 1.2% granted plus 0.5% GVR, and the rationale's own anchor is a grant-family rate, so the comparison mixes two definitions. And "did not file a brief in opposition, effectively waiving a response" overstates what the snapshot shows: there is no waiver entry, only the absence of a response at distribution, which is consistent with a waiver but is not one. Neither point changes the direction of the adjustment. The closing sentence on a possible response request is a reasonable residual uncertainty. The score reflects a correct but thin analysis that leaves the strongest argument unmade.

## Leakage

Forward cell. Every call in the log is `unobserved` (capture coverage 0.0, the engine's standing shape), so each is graded on its query: reads of the provisioned record, the prompt, the schemas, and three statpack greps. No web, MCP, or corpus call. Nothing in the reasoning presupposes the outcome. `retrieved_outcome_material: false`, `influenced_prediction: not_applicable`, `leakage_suspected: false`.

## Big case

My own read, formed before consulting the candidate's score, is 0.08. The candidate's 0.1 is close, for the same reasons: a routine, fact-bound state criminal appeal with no broader federal interest.
