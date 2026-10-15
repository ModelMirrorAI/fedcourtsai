# Evaluation: codex-baseline

## Outcome and numerical score

The committed outcome records a plenary certiorari grant on October 13, 2026: `actual_disposition = granted`, `actual_granted = 1`. The provisioned October 14 snapshot, whose source creation stamp is October 13, records a second distribution on October 5 for the October 9 conference and the October 13 grant. These are evaluation-time facts, not information attributed to the October 3 prediction.

The predicted label `granted` matches exactly: **correct = 1**. With P(grant) = 0.78, **Brier = (0.78 - 1)^2 = 0.0484**. This is a cert cell, so no vote accuracy or judgment score is supplied. The structured claims and forecast document are not graded here; claim scores belong to the harness. No semantic set is declared at this stage.

The prediction froze `context.band = federal`, `salience_version = sal-v4`, and Term 2025. The harness supplies the stamped segment base rate, basis, and Brier skill; I leave those fields absent and do not substitute a hand-pooled baseline.

## Reasoning quality: 0.88

The rationale clearly distinguishes the provisioned docket, retrieved antecedent opinion, unavailable petition papers, and its own inferences. It identifies a review-worthy statutory dispute and a divided published decision without treating disagreement with the agency as sufficient proof of a square circuit split. It explains the competing organizational-support and terrorist-activity formulations, acknowledges narrower factual and remand considerations, and expressly avoids double-counting the government's participation after selecting the federal-band anchor.

Its baseline method selects the reached population under the frozen salience version, restricts the displayed Term rows to those preceding the prediction's Term, and distinguishes terminal relist/CVSG tables from prospective transition probabilities. The committed table consulted for this evaluation supports that methodological distinction; it is not used to replace the harness's anchor.

The limitations are real but well disclosed: the actual petition, opposition and question presented were unavailable, the asserted inter-circuit tension was not independently established as a square split, and the adjustment to the headline probability remains qualitative rather than empirically estimated. These prevent a near-perfect score. The grade reflects the soundness and evidentiary discipline of `reasoning.md`, not the correctness of unscored forecast details or the eventual grant alone. I did not independently retrieve the lower-court opinion to verify every doctrinal paraphrase.

## Leakage assessment

Both frozen context and captured log identify forward mode. The October 3 prediction predates the October 13 resolution. External queries target the September 2025 Fourth Circuit opinion; the CourtListener search includes a pre-petition date restriction. The lower court's grant of agency review is not this certiorari outcome.

The log reports result-capture coverage of approximately 0.931. Its two web attempts have unobserved results, so their null dates do not establish failed or empty retrieval. Their query scope, the remaining call rows and the reasoning provide no evidence of this petition's eventual disposition surfacing. Accordingly, `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`. This is an assessment of the visible record, not a guarantee about uncaptured content.

## Stakes

My provisional stakes assessment is 0.60: a nationally consequential statutory immigration issue with serious consequences for affected applicants, but no demonstrated broad constitutional holding. It is the same case-level read used for every candidate, not a score for agreement with a candidate's number.
