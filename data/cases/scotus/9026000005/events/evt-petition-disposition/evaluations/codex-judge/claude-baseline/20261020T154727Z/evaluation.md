# Evaluation: claude-baseline

## Outcome and mechanical scores

This is a cert-stage petition-disposition cell. The recorded outcome is denial on October 19, 2026, with `actual_granted = 0`. claude-baseline predicted `denied`, so `correct = 1`. Its grant probability was 0.08, giving a Brier score of `(0.08 - 0)^2 = 0.0064`. A denial does not establish the Court's agreement with any proposed merits rationale.

The scored prediction froze an elevated band under sal-v4 for Term 2026. The stamped segment base rate and its associated skill and provenance are the harness's responsibility; those evaluator fields remain null pending stamping. No alternative baseline is calculated or quoted here. Cert votes are never scored. No semantic grading is declared for this stage, and the quantitative claims are left to the harness.

## Reasoning quality: 0.90

The rationale gives a strong case-specific explanation rather than treating a low grant probability as self-justifying. It connects the intervening removal precedent described in the opposition to the government-favorable judgment below, explains why that alignment reduces the need for a GVR, and identifies the closely related Harris denial as a comparator rather than this petition's own outcome. The provisioned opposition supports those central descriptions and expressly requests denial or summary affirmance.

The analysis also engages the competing agency-specific argument: separating the NLRB's adjudicatory work from prosecution could matter if an adjudicatory carve-out remained available. It recognizes the requested response as a positive attention signal, distinguishes redistribution after a response request from demonstrated post-conference relisting, and remembers that a grant followed by summary affirmance is still a grant. These are sound distinctions regardless of the eventual denial.

The principal limitations are the judgmental size of the adjustment from its selected population anchor, reliance on a single companion denial that supplies no merits holding, and categorical wording that there is nothing to remand for despite acknowledging a possible carve-out. The candidate discloses that it inspected selected passages rather than the entire retrieved related opinion and could not establish whether Harris drew a writing. The score grades only `reasoning.md`; neither the forecast document nor the structured claims receive a separate or implicit score. In particular, the absence of a noted dissent in the actual outcome does not lower this reasoning grade.

## Leakage assessment

The prediction context and captured log both identify forward mode. All 30 calls are dated September 30, 2026, before the target petition's October 19 resolution, with result-capture coverage 1.0. The logged CourtListener searches and opinion access concern Slaughter and Harris; the dated Slaughter result is June 29. The reasoning openly describes those related developments, which are legitimate forward signals, not this petition's disposition. The broad granted-case corpus query does not target this denied petition. A failed example-artifact command in call 13 supplies no affirmative evidence of retrieved outcome material.

No logged query, recorded document date, or supplied prose indicates that this petition was already decided when forecast. Result digests do not expose the complete returned bodies, so this is an assessment of the available audit record, not a claim to have independently reread the retrieved opinion. `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, and `leakage_suspected = false`.

## Stakes

My case-level significance read is 0.80: the questions implicate presidential control of an important national adjudicator and the institutional operation of labor law. The intervening precedent described in the filings limits the novelty of this particular follow-on petition. This assessment concerns stakes, not grant probability, and does not treat denial as a merits ruling.
