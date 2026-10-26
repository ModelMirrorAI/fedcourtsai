# Evaluation: codex-baseline

## Outcome and numerical scores

This is a cert-stage cell. The authoritative outcome is `dismissed`, with `actual_granted = 0`, resolved October 20, 2026. The provisioned October 26 snapshot records a joint Rule 46 dismissal stipulation on October 19 and dismissal on October 20. It does not establish why the parties agreed to dismiss.

The prediction named `denied`, so exact-label correctness is **0**: dismissal is not denial. Its 0.24 probability of any grant gives **Brier = (0.24 - 0)^2 = 0.0576**. It favored the correct non-grant binary but missed the disposition route. The frozen prediction carries `baseline` under `sal-v4`; the segment anchor and skill are left to the harness. Any comparison is to the stamped segment base rate, not a separately pooled evaluator rate. Cert votes are not scored; no judgment or semantic grade applies. Mechanical claim scores and the forecast document are not graded here.

## Reasoning quality: 0.87

The grade concerns only `reasoning.md`, not whether its forecast happened to win. The analysis identifies the actual source-of-law question, separates grant-family relief from plenary review, and ties the follower posture to the petition's express hold request on pages 9-10. It examines the appended lower-court contract reasoning instead of accepting the petition's framing wholesale. Particularly strong are its distinction between a claimed 4-1 conflict and the narrower disagreement it actually checked, its treatment of the unseen opposition as a limitation, and its refusal to infer later docket action from a stale snapshot.

The main weakness is quantitative rather than doctrinal: the move to 0.24 remains a substantial judgmental uplift without a fitted conditional estimate. The companion's current posture is deliberately unverified, leaving a load-bearing dependency unresolved. Those limitations justify a deduction, but the subsequent voluntary dismissal does not invalidate otherwise careful pre-decision legal analysis. This grade does not score the separate forecast or individual structured claims.

## Leakage and significance

The prediction and captured log say `forward`; prediction creation was October 6, before the October 19 stipulation and October 20 dismissal. The historical research targets were the 2020 GE Energy and 2021 Setty decisions. No query or staged prose shows this petition's own disposition as already decided. The log captures 39 of 42 call results; its three web attempts are unobserved, not independently established as empty. That uncertainty is acknowledged without treating missing telemetry as leakage. Assessment: outcome material not observed, influence `not_applicable`, `leakage_suspected = false`.

My independent significance assessment is **0.32**: a nationally relevant but technical arbitration question in a derivative private-insurance vehicle, ending without a Supreme Court merits ruling.
