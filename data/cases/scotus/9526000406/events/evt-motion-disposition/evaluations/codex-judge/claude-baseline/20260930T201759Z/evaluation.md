# Evaluation: claude-baseline

## Outcome and numerical score

This is an interim application, not a cert or merits cell. The supplied outcome records an unqualified grant on September 29, 2026, with `actual_granted = 1`. The September 29 provisioned snapshot confirms the stay and also records a grant of certiorari; that additional action does not change this event's interim scoring axis. claude-baseline predicted `granted` at 0.74, so `correct = 1` and the Brier score is `(0.74 - 1)^2 = 0.0676`.

## Reasoning quality: 0.84

The rationale identifies the correct substantive stay target, distinguishes it from administrative relief, and develops a persuasive case-specific explanation for departing from the heterogeneous application baseline. It treats prior intervention in this litigation as relevant without completely overlooking the changed final-judgment posture. Its discussion of declaratory relief, vacatur, additional statutory grounds, and mixed-relief risk supplies meaningful reasons against certainty. The probability decomposition makes the downside explicit.

The principal limitations are evidentiary and calibration-related. The proposed 0.7–0.8 government-applicant anchor is not established by the five-application sample described, and the stated broader emergency-docket pattern is partly recollection. The rationale sometimes treats the government's disruption account and the implications of earlier interim orders more definitively than their evidentiary status warrants. It gives less attention to respondents' potential irreversible harms than to governmental equities. These limitations constrain the grade despite the correct result. The supplied application supports the changed remedial posture, but this short disposing order does not establish that the Court adopted the candidate's particular legal explanation.

Only `reasoning.md` receives this qualitative grade. The forecast document was read for context; its timing, cert-treatment prediction, proposed rationale, and vote lineup are not independently scored or folded into reasoning quality. Quantitative claims remain for the harness, and no semantic block is declared on this interim event.

## Baseline and other omissions

The baseline and skill are harness-owned and are deliberately absent from the JSON; `base_rate_basis` is null. The committed statpack supplied to this evaluation has an interim section and 296 resolved substantive applications across its nonzero strictly-prior 2024 and 2025 rows, clearing the stated 50-resolution floor for the prediction's frozen application Term 2026. No missing-section or thin-pool refusal is apparent. This is a reading of the supplied pack, not a refreshed corpus claim; remote freshness was not established. Uneven parsing and the escalation-selected scored population limit interpretation. No post-run stamped rate has yet been observed. Votes are never scored on interim cells, even though this candidate supplied them and the docket notes disagreement.

## Leakage

The harness log records forward mode and full result-capture coverage, with calls on September 27. The candidate's live-docket reading explicitly stops at the response request. Its earlier disposing orders refer to 24A1153, not this application. The later-on-opening-day response request lies outside the provisioned arrival baseline but is legitimate unrestricted forward information. Neither the logged queries nor the prose show this application's September 29 outcome already known. The assessment is therefore `not_applicable`, with `retrieved_outcome_material = false` and no leakage exclusion. Captured-result metadata and prose support this assessment; digests are not a reproduction of every retrieved page.
