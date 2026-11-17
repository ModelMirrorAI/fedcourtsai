# Evaluation: codex-baseline

Cert-stage cell, forward mode. Outcome: **denied** on 2026-11-16 after one distribution, no CVSG, no noted dissent.

## Scores

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.12 - 0)^2 = 0.0144.
- The segment base rate, skill and basis are the harness's to stamp; left null.

## Reasoning quality: 0.70

This is careful work that landed on the wrong side of the anchor. The strengths:

- It reads the lower court's venue analysis in the appendix (App. 13-17, 35-36, 60) instead of relying on the petition's account of it.
- It checks *Abouammo* and *Lawrence v. Chater* at source and states the *Lawrence* standard accurately.
- It handles the statpack cuts correctly, treating terminal relist and amicus buckets as descriptions of where petitions ended, not as forward probabilities.
- Its docket facts are right (waiver October 21, distribution October 28).

The weakness is the net adjustment. The document itself lists the waiver, the rehearing denial with *Abouammo* in front of the panel, the statutory distinction and the forfeited instruction argument, then still moves to more than double the stamped segment base rate on the strength of the two-day timing. With the government declining even to respond, those negatives warranted a figure at or below the anchor. It says candidly that the adjustment is judgment and not a measured rate, which is a point for it. Denial stayed clearly modal, so the cost was modest.

## Predicted reasoning: 0.7

Central claims: denial; zero additional distributions; a modal disposition window opening November 16; no separate writing; no CVSG. All are borne out, and the timing window was hit on its first day. The document is specific on path and timing. It stays short of the top anchors because the path it called is the default for a waived, baseline-band petition, and the no-CVSG claim was close to entailed by the posture. The conditional content on a GVR and what a remand would leave open never came into play and earns neither credit nor penalty.

## Leakage

Forward cell, predicted 2026-11-01. The log is 93% captured. It shows the provisioned files, the statpack, corpus GVR queries limited to prior Terms, and CourtListener reads of *Abouammo* and *Lawrence*. Three web-search rows are `unobserved`; their queries target the *Abouammo* opinion, not this petition, and the candidate reports they returned nothing. Nothing shows the disposition surfacing. `influenced_prediction` = `not_applicable`.

## Big case: 0.10

A fact-bound GVR request in one tax-preparer prosecution, with no amici and a government waiver.
