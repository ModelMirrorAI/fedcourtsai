# Evaluation of codex-baseline — St. Clair v. Pettit, No. 25-1274 (cert stage)

## Outcome and scores

The petition was denied on October 5, 2026, after a single distribution for the September 28 long conference, with no response called for and no noted dissent. Cert cell; `outcome.actual_granted` = 0.

| Field | Value |
| --- | --- |
| predicted_disposition / actual | denied / denied → `correct` = 1 |
| probability | 0.04 |
| brier_score | 0.0016 |
| segment_base_rate | 0.0512 (`risk_set`) |
| brier_skill_score | 0.390 |
| reasoning_quality | 0.85 |

**Base rate.** The prediction froze `band: baseline` under `salience_version: sal-v4`, and the statpack's band table heading is sal-v4, so the basis is `risk_set`: the bracketed `reached` figure for `baseline`, pooled resolved-weighted over every rendered Term strictly before OT2025 (OT2017–OT2024, n = 11,580), is 5.12%. The table renders all ten Terms the pack holds, so the rendered window and the pack's window coincide and there is no lookback divergence to flag. `judgment_correct` is null (not a merits cell); `vote_accuracy` is omitted (cert votes are never scored).

## What the reasoning got right

- **Anchor done properly.** Pooled the sal-v4 baseline reached rate over OT2017–OT2024 from the committed pack, named the number (5.12%) and its basis, and explicitly kept OT2025 and OT2026 out. It also read the terminal relist and CVSG cuts and correctly declined to treat them as forward hazards.
- **Verified the split rather than taking the petition's word.** Read Dulworth v. Evans (10th Cir. 2006) on CourtListener, confirmed the Cox v. McBride disagreement, and noticed the section 2241 / 2254 classification wrinkle that makes the split messier than the petition presents it.
- **Distinguished Bowe on the text.** Read Bowe's syllabus and identified why its 2244(b) cross-reference analysis does not transfer to 2244(d)(1), whose trigger is custody pursuant to a state judgment, a status the petition itself concedes. That is the point the Court's denial is consistent with, and it is the right reason to discount the requested GVR.
- **Vehicle read.** Unpublished COA denial, decades-long interstate custody oddity, relief that would not follow even from a favorable limitations holding, no docket attention. Landed modestly below the anchor rather than inflating on the word "split."
- **Honest limits.** States that its lower-court account comes from the petition's advocacy, that it did not survey the circuits' later treatment, and that it could not tell whether the rehearing court considered Bowe.

## Where it falls short

- It says the event's "omitted stage does not make it a merits event," but `event.yaml` records `stage: cert` explicitly; a small misread of the provisioned record with no effect on the number.
- The split adjustment is described as upward and then "tempered," yet the final number sits below the anchor; the write-up could have stated the net direction and size of each adjustment more plainly.
- It did not retrieve the lower-court orders that were available (the E.D. Okla. opinion and the Tenth Circuit docket), which would have confirmed the untimeliness-under-any-trigger posture rather than relying on the petition's framing.

Reasoning quality 0.85: well anchored, doctrinally careful on the one question that mattered (whether Bowe reaches 2244(d)), candid about limits, with only minor slips.

## Leakage

Forward cell. The prediction was created September 16, 2026 against a September 16 snapshot; the event resolved October 5. The log shows record and statpack reads, three unobserved web searches aimed at Bowe and Dulworth (graded on their queries, which name neither this petition nor its docket), and CourtListener reads of those two opinions. No retrieved document is dated at or after the resolution, no query seeks this petition's disposition, and no `data/qp-topics/` path appears. The reasoning treats the September 28 conference as pending. `influenced_prediction` = `not_applicable`, `leakage_suspected` = false.

## Big case

My own read is 0.15. The legal question has some systemic reach for state-prisoner habeas timing, but the split is old and shallow, the decision below is unpublished, the custody claim is idiosyncratic, and the petition was denied on its first list with no response and no writing. The predictors' scores are visible in the staged `prediction.json`, so I could not form this read without having seen them; I formed it from the record and outcome and record that caveat rather than claim a blindness I did not have.

Semantic grades: none, this is a cert cell and no semantic set is declared. `claim_scores`: harness-computed, not written here.
