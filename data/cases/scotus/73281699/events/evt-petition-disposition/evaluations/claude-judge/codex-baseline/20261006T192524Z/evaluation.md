# Evaluation of codex-baseline — Cohen v. Judicial Conduct Board of Pennsylvania (No. 25-1215), evt-petition-disposition

## Outcome and scores

Cert-stage cell (`event.yaml` stage `cert`, moment `distribution`). The petition was **denied** on 2026-10-05 after the September 28 long conference, with no noted dissent and no further distribution beyond the two already on the docket (`actual_granted` 0, `distribution_count` 2).

- `correct` = 1: `predicted_disposition` `denied` matches `actual_disposition` `denied`.
- `brier_score` = (0.25 − 0)² = **0.0625**.
- `segment_base_rate` = **0.1724**, basis `risk_set`. The prediction's frozen context carries both `band` `elevated` and `salience_version` `sal-v4`, and the statpack's *Segment base rate by salience band (sal-v4)* heading names the same version, so the bracketed `reached` figure applies. Pooled resolved-weighted over every rendered Term strictly before this case's Term 2025 — 2017 through 2024 (the 2026 row is empty) — the eight rows give 484.4 / 2810 = 0.1724. The caption states "Most recent 10 of 10 Term(s)", so the rendered window is the pack's whole window and no lookback divergence needs flagging.
- `brier_skill_score` = 1 − 0.0625 / 0.1724² = **−1.103**. The forecast was worse than the naive band baseline: it moved up from the anchor on a petition that was denied.

## What the prediction got right and wrong

Right: the modal call (denial, no separate writing, no CVSG, plenary rather than summary route if granted) and the baseline work. The candidate pooled the correct table, the correct figure (bracketed reached, not terminal), the correct window (2017–2024), and reported the weighted denominator — exactly the leakage-safe cut the contract asks for. It read the two distributions correctly as a response-request interruption plus post-briefing redistribution rather than a substantive relist, and it refused to treat terminal relist-bucket rates as forward hazards.

Wrong in direction: it set P(grant) at 0.25, about eight points above the 0.172 anchor, and the case was denied without comment. The upward reasons were real (response requested after a waiver; a federal constitutional standard squarely decided by a state court of last resort; a reply that sharpened the Jenevein disagreement). But the candidate's own analysis listed the full set of vehicle problems — six disciplinary rules, the alternative strict-scrutiny holding below, the retired petitioner, the trappings-of-office facts that even Jenevein would sanction — and then weighted them less than the attention signals. The retrieved reply brief appears to have moved the number up; a reply is the petitioner's best case and should carry less weight than the candidate gave it.

## Reasoning quality: 0.72

Strengths that drove the score up: disciplined, well-documented, and candid. The information-set section states what was read, what was retrieved, and why the September 17 snapshot filename does not prove a fresh docket. Jenevein was independently checked on CourtListener rather than taken from the parties, and the candidate correctly noted that Jenevein both supports a standards disagreement and undercuts the vehicle. Each secondary number was given a stated rationale and its conditioning made explicit. No facts were invented; limitations were listed.

What held it down: the final calibration. The analysis identified the reasons the Court would prefer a cleaner case and then under-weighted them against a response request, which is a common signal on paid petitions and not strongly predictive of a grant on its own. The writing is also somewhat over-hedged, with many sentences that qualify rather than conclude, which makes the actual weighing hard to follow.

## Leakage

Mode `forward`; the case was pending at the 2026-09-17 snapshot and resolved 2026-10-05, so ordinary retrieval could not have leaked the outcome. I checked anyway: the log's 30 calls show provisioned-record reads, a Jenevein web search and two CourtListener calls on the 2007 opinion, and two opens of the August 3 reply brief at the exact PDF URL already linked from the provisioned docket. The three web rows are `unobserved`, so they are graded on their queries, none of which names this petition's history or disposition. No `retrieved_doc_date` on or after resolution, no `data/qp-topics/` path, no outcome reference in the prose. `retrieved_outcome_material` false, `influenced_prediction` `not_applicable`, `leakage_suspected` false.

## Big case

My independent read is 0.35. The question — whether content-based limits on a sitting judge's non-campaign political speech draw strict scrutiny — is a genuine open question for a large professional class, and the court below invited this Court's resolution. But the petitioner is a mandatorily retired judge whose suspension is served, the sanction rested on six rules including use of the robe and title, no amicus appeared, and the denial drew no noted dissent. Moderate doctrinal stakes if granted, low public salience, weak vehicle. The predictor's score sits in the staged `prediction.json`, so I read it before writing this; the read above rests on the record rather than on that number.

## Not scored here

`claims`, `predicted_reasoning.md`, and the noted-vote fields are outside this grade by contract; `claim_scores`, `process_version`, and `base_rate_salience_version` are the harness's.
