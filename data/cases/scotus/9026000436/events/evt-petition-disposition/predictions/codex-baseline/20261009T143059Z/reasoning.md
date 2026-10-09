# Rationale for the forecast

## Inputs and information boundary

This is a forward, cert-stage distribution cell for Radiall USA, Inc. v. Gary T. Ramadei, docket 26-436. I used the provisioned event, `record/context.json`, `record/snapshots/2026-10-09.json`, `documents.json`, the questions-presented text, and selected portions of the petition: its statement and cert arguments, including the preservation argument, and the reproduced Second Circuit order at Appendix A, especially pages 2a-5a. The frozen context is `baseline`, `sal-v4`, Term 2026, with one distribution and no CVSG. The snapshot's latest proceeding is the October 7 distribution for November 6; it records the respondent's October 5 waiver, not an opposition brief or a requested response. The July extension concerns time to file and is not a grant of certiorari.

The document manifest marks the 180-page petition source as truncated. The questions presented and relevant appellate preservation discussion are available, but I have not assumed access to the complete trial record or appendix. There is no provisioned brief in opposition, consistently with the waiver shown on the docket. The petition's characterization of other circuits is advocacy, not an independently verified circuit census. I did not retrieve this petition's current docket, disposition, subsequent history, or other predictions and have no known outcome for it.

## Empirical anchor

The committed statpack's salience table matches the frozen `sal-v4` version. Pooling the **bracketed reached** rates for the private-petitioner `baseline` band over every displayed strictly prior Term, **2017-2025**, gives **642 grant-family outcomes / 12,871 denial-reweighted resolved petitions = 4.98796%**. I computed this from `metrics/statpack.json` using each corresponding segment's `prefix_est_grant_rate` and `prefix_weighted_resolved`, rather than averaging rounded percentages. I excluded Term 2026 and did not substitute the much lower terminal-baseline rate.

This is the committed pack last changed in commit `3f3ca14f4` at **2026-10-08T21:56:24Z**, not a fresh live-corpus query. That timestamp is artifact vintage, not the corpus-wide newest pull or snapshot; those were not independently established in this cell. The case-specific baseline is dated October 9, 2026, with proceedings through October 7. The pack's modern-cert and originating-circuit cuts provide context, but the class-appropriate reached pool is my numerical anchor.

The paid-segment relist cut shows sharply higher grant rates among petitions that ultimately accumulate multiple relists; the CVSG cut also shows strong selection. These are terminal buckets, not transition hazards from this petition's one-distribution state. I do not turn their grant rates into estimates of another distribution or a future CVSG.

## Why 7%, rather than the anchor or a split-driven high estimate

The first question is a meaningful upward signal. The petition identifies competing causation standards for a nationwide employment statute, including the Second Circuit's Woods rule and contrary approaches in the Fourth and Eleventh Circuits. A jury actually applied the motivating-factor standard, so this is not merely an abstract dispute about terminology. The companion question about preserving challenges to precedent after Loper Bright adds potential significance. Those features justify treating this as more certworthy than a generic private petition.

The dominant downward adjustment is vehicle quality. Appendix A, pages 3a-5a, does not simply refuse to consider a newly available legal argument. It identifies affirmative invitation of the instruction, failure to contest the standard in October 2024 post-trial motions after Loper Bright, and failure to establish plain error in a legally unsettled area. The earlier causation decisions invoked by petitioner also predated the litigation. The futility argument must therefore overcome more than one independent preservation rationale. The petition's reliance on Dupree concerns extending a rule about a legal issue already raised at summary judgment to a challenge the panel says was never raised in the district court. That is an additional contested step, not a clean application of the petition's preferred substantive rule.

I separately checked Loper Bright, 603 U.S. 369, 412-413 (2024), through CourtListener's opinion text. Its discussion preserves statutory stare decisis for earlier agency-action holdings and rejects reliance on Chevron alone as sufficient justification for overruling them. This supports discounting an automatic-remand theory; it does not prove the Second Circuit's FMLA interpretation correct or foreclose review on independent textual grounds. Loper Bright was already available to the panel, so it is not a newly intervening development after the judgment under review.

I therefore settle at **P(any grant) = 0.07**, with denial as the modal disposition. The increase over 4.99% reflects a recurring statutory conflict; the modest size of that increase reflects the unusually visible preservation barrier, the summary-order posture, and the absence of any affirmative Court interest beyond a first distribution. A respondent's waiver is not itself the Court's merits assessment. The principal uncertainty is whether the Justices regard the preservation question as an independently review-worthy issue rather than a reason to await a cleaner FMLA vehicle.

## Other probabilities and stakes

The **20%** additional-distribution probability allows some interest in the split or a requested response but keeps no further distribution as the modal path. The **2%** CVSG probability recognizes the Department of Labor's regulation without mistaking a federal statutory issue for a likely invitation. The **25%** summary route is conditional on a grant, not an unconditional probability; a procedural remand remains possible, but plenary review is the more plausible grant route. The **4%** writing probability is conditional on denial and concerns only the existence of any dissent or statement. These secondary probabilities are judgmental estimates, not fitted hazards or purported published baselines.

The **0.56 stakes score** reflects the nationwide practical significance of the causation rule and a potentially recurring preservation issue. It is separate from the low probability that this particular vehicle is selected. I omit cert votes because the record does not support meaningful individual predictions.

## Tool limitations

Two general-precedent web retrieval attempts returned no usable content. CourtListener MCP successfully supplied the pertinent Loper Bright passage. A first local CLI invocation failed because its default cache directory was read-only; using a writable temporary cache allowed the path command to run. Neither limitation blocked the forecast. The incomplete petition text is recorded in `flags.json` for durable visibility.
