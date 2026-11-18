# Evaluation — claude-baseline, scotus/9026000210, evt-petition-arrival-disposition

**Stage:** cert (arrival moment). **Outcome:** petition denied on 2026-11-16, after a single distribution (conference of 2026-11-13), with no noted dissent or statement.

## Scores

- Predicted `granted` at P(grant) = 0.8; actual `denied`. `correct` = 0.
- `brier_score` = (0.8 − 0)² = 0.64.
- `vote_accuracy` omitted (cert cell). The segment base rate, its basis and the skill score are the harness's to stamp and are left null; no semantic set is declared on a cert cell, so there is no `semantic_grades` block.

## Reasoning (`reasoning_quality` = 0.5)

The most thorough rationale of the three, and still wrong. The anchor is correct and correctly computed against the statpack build in force when the candidate ran (rebuilt with `statpack-at`, build 02dd6a20fccc): the federal-band risk-set column pooled over OT2017–OT2025 gives about 143 of 201, ~71%, cross-checked against the band table's granted 48.8% + gvr 22.4%. It also spotted something real in the pack — the two most recent Terms run 52–60% on larger federal-band counts — and correctly read that as a reason the pooled anchor may overstate the current class. Its downside list names the interlocutory posture and the lurking Tucker Act channeling question, and its predicted denial path ("posture-based") is the most plausible reading of what happened. The failure is in the weighing. Having identified recent-Term dilution toward the mid-50s and two concrete vehicle problems, it nonetheless went nine points *above* the pooled anchor, leaning on the petition's own account of its vehicle quality ("no disputed facts," "single QP") without a brief in opposition to test it, and on an inference from the 2025 emergency-docket grant rulings that interim-relief receptivity translates into a cert grant from a preliminary-injunction posture — an inference the outcome did not bear out. "Main uncertainty is timing-shape, not direction" was the overconfident sentence. Its 0.30 dissent-from-denial was also on the high side of what occurred. Strong method and the right risks named, offset by a mis-weighted upward adjustment: 0.5.

Base-rate figures were checked against the statpack build the candidate was placed against (`statpack-at`: build 02dd6a20fccc, landed 2026-08-19, no alternative build), not the currently committed pack.

## Predicted reasoning (`predicted_reasoning_quality` = 0.15)

Central claims: grant with plenary review and a timetable (the document's lead, in bold), an extension pushing distribution to a November or December conference, one to two relists, the question taken as written and plenary over summary disposition (conditional on a grant; neither credit nor penalty), and a denial branch — posture-based, 30% chance of a noted writing. The lead call failed, costing most of the grade. The extension-and-timing forecast was specific and correct (extension to October 19; conference of November 13). The relist forecast failed: the petition was disposed of after its first conference. The denial branch is consistent with the silent denial but hedged, and the bare order cannot confirm the posture rationale, so it is unresolved rather than credited. No-CVSG is entailed. The conditional merits outlook never came into play. A failed central call with the resolvable secondary claims split: 0.15.

## Leakage

Forward cell, run the day after docketing and about three months before the denial. Forward cell: predicted 2026-08-20, the day after docketing; the petition was denied 2026-11-16. Log: 26 calls, result capture coverage 1.0: shell reads of provisioned inputs and the committed statpack, plus one `fedcourts query --citation "500 U.S. 173"` (Rust v. Sullivan, a 1991 authority) that returned no rows. Reliance on the 2025 grant-termination stay rulings is disclosed as general knowledge predating the snapshot and is legitimate forward signal about other cases. No retrieved_doc_date on or after resolution, no read under data/qp-topics/, no order or opinion resolving this petition cited, and the reasoning nowhere presupposes a result (it forecast the opposite). Confirmed genuinely unresolved at prediction time. `influenced_prediction` = `not_applicable`; `leakage_suspected` = false.

## Big case

My own read: 0.6. Solicitor General petition on whether the First Amendment bars viewpoint-based termination of competitive federal research grants; a classwide preliminary injunction against a flagship executive policy, with many parallel suits. The subject matter is nationally significant, but the Court denied review at the first conference with no noted dissent or statement, leaving an interlocutory Ninth Circuit ruling in place and deciding nothing; the question remains open for a later final-judgment vehicle. High-stakes subject, modest realized significance for this docket.
