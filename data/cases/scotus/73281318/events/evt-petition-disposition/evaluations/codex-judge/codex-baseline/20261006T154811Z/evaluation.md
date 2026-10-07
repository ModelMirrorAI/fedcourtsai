# Evaluation of codex-baseline

## Outcome and numerical scores

The staged prediction from run 20260916T170237Z is evaluated on the cert axis. The supplied outcome records denied, actual_granted = 0, on October 5, 2026. The predicted denied label is correct (1), and the 4% grant probability yields (0.04 - 0)^2 = 0.0016. The denial does not itself establish a merits holding or explain which vehicle objection mattered to the Court.

The frozen prediction context is elevated under sal-v4, Term 2025. The committed metrics/statpack.md sal-v4 table supports a risk_set baseline using its bracketed reached rates for every displayed Term strictly before 2025. For 2017–2024, the (rate %, weighted n) pairs are (17.5, 400), (15.9, 347), (13.8, 334), (16.1, 397), (20.5, 342), (19.0, 300), (17.5, 354), and (17.9, 336). Weighted pooling gives 484.386 / 2,810 = 0.17237935943060498. Hence skill = 1 - 0.0016 / rate^2 = 0.9461544946048972.

This uses the rendered, rounded percentages as instructed, rather than reconstructing the unrounded JSON calculation the candidate reports. The difference from its 484 / 2,810 anchor is rounding, not an analytical error. The table describes denial-reweighted live/historical-slice estimates and renders 10 of 10 Terms; there is no shortened displayed window to flag. The evaluator's terminal context and Terms 2025–2026 supply no baseline inputs. No live corpus lookup or corpus-freshness claim is involved.

## Reasoning quality: 0.93

The rationale is unusually explicit about both the source and limits of its inferences. It anchors to the appropriate frozen risk set, avoids treating terminal relist statistics as transition hazards, and connects the downward adjustment to the interlocutory posture and application-specific framing. It discusses the petitioner's favorable facts alongside the opposition's cumulative circumstances rather than simply accepting one brief. The supplied opposition supports its account of the finality issue and of why Case's treatment of probable-cause language may not change the lower result.

It distinguishes a response request from actual merits relisting and recognizes that an unavailable reply might answer the finality objection. It treats the earlier precedent through the supplied briefs after unsuccessful external verification, rather than pretending the independent verification succeeded. The small remaining GVR possibility is presented as uncertainty, not as a demonstrated entitlement to remand.

The main limitation is that the particular 4% estimate remains a judgmental adjustment, not an empirically calibrated conditional estimate; the rationale candidly says so. Independent authority verification and the reply are unavailable. Those limitations prevent an unqualified score, but the grade does not reward the lower realized Brier score or infer from denial that every proposed rationale was correct.

Only reasoning.md's soundness is graded. The separate forecast and structured mechanical claims are not scored here. The harness owns claim_scores; cert-stage votes and semantic claims receive no grading blocks.

## Leakage

The prediction and log identify forward mode on September 16, before the October 5 denial. Result capture is 27/29. The two unobserved web rows cannot substantiate the prose's assertion of empty results; I assess their queries instead. They seek Case v. Montana and its PDF, not this petition's subsequent history. The remaining logged work concerns provisioned inputs, aggregate rates, precedent research, or output administration. A path-excluding instructions search is not a read of the excluded labeling artifacts. No call or rationale reveals this petition's own disposition as already known. Retrieved outcome material is therefore false, influence not_applicable, and leakage_suspected false, with the capture limitation retained rather than hidden.
