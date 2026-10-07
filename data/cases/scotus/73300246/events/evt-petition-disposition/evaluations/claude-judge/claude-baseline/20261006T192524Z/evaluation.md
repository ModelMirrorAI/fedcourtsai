# Evaluation of claude-baseline — scotus/73300246, evt-petition-disposition

## Outcome and scoring

Cert cell (`event.yaml` stage `cert`, kind `petition`, moment `distribution`). The petition in No. 25-1254, Harvey v. City of Reno, was distributed once (June 24 for the September 28, 2026 conference) and **denied on October 5, 2026** with no noted dissent and no CVSG (`outcome.json`: `actual_disposition: denied`, `actual_granted: 0`, `distribution_count: 1`).

- `predicted_disposition: denied` → **correct = 1**.
- `probability: 0.015` → **brier_score = 0.000225**.
- **segment_base_rate = 0.0512**, basis **`risk_set`**. The prediction's frozen context carries `band: baseline` with `salience_version: sal-v4`, and the statpack's "Segment base rate by salience band (sal-v4)" heading matches that version. I pooled the bracketed `reached` figure for `baseline`, weighted by its `n`, over every rendered Term strictly before this case's Term (OT2025): OT2017 through OT2024 (4.7/1643, 4.6/1524, 4.6/1399, 4.5/1739, 5.6/1500, 5.8/1192, 5.9/1312, 5.7/1271), giving 5.12% over n = 11,580. The caption states "Most recent 10 of 10 Term(s)", so the rendered window is the pack's whole window and there is no lookback divergence to flag.
- **brier_skill_score = 0.9142** (1 − 0.000225 / 0.0512²).
- No `vote_accuracy` (cert stage; the empty vote block is correct and unscored). No `semantic_grades` (no semantic set on a cert cell). `claim_scores` and `process_version` are the harness's.

## Reasoning quality: 0.86

This is a sound and well-disciplined rationale. Its strengths:

- **Correct anchor, correctly derived.** It takes the frozen `baseline`/`sal-v4` band, matches it to the right table, pools the bracketed `reached` figure over OT2017–OT2024 and arrives at ~5.1% — the same number I computed as the scoring baseline. It explicitly declines the terminal rate for a live petition.
- **The vehicle analysis is right and tracks why the Court denied.** It identifies the three things that made this petition a non-starter: an unpublished state-court order of affirmance on a pleading-stage dismissal; an independent state-law limitations holding sitting beneath the property-interest ruling (an adequate-and-independent-ground problem); and a contested factual premise (the BIO's point that the parcel still abuts Huffaker Place, so "landlocked" is disputed). It also notes the petition's own concession of merely permissive use and its candor that the Court "has not unequivocally held" the proposition sought — read correctly as a first-impression ask, not a split.
- **Selection signals read correctly.** Solo practitioner, no amici, three of four respondents waiving, one routine distribution to the long conference. I checked the statpack claim it leans on: the originating-court table does show `nev` at 20 resolved, 100% denied, and the candidate rightly treats that as a thin cell and leans on the general state-court pattern instead.
- **Honest counterweight.** It names the one thing that could have moved the number (the Court's recent takings appetite and the Tyler framing) and prices it, then states where to discount its own read.

Minor weaknesses: the 3.5-fold discount from the anchor is a judgment call stated as such but not otherwise grounded; and the rationale spends some words on the summary-route and relist claims, which are not part of this grade. Neither detracts from the soundness of the analysis of the disposition itself.

## Leakage: not applicable (forward)

Mode is `forward` in both the log and the frozen context; the prediction was created 2026-09-16, before the September 28 conference and the October 5 denial. All 27 calls are captured. The only outward call was one `fedcourts query` over 2020s SCOTUS rows, disclosed in `retrieval.md` as a connectivity check whose rows were unrelated. No CourtListener or web call, no query naming this docket's disposition, no `retrieved_doc_date`, no read of `data/qp-topics/`. Nothing suggests a decided case was provisioned forward. `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, `leakage_suspected = false`.

## Big case

My independent read is 0.10: a fact-bound, local access dispute from an unpublished state order, denied without comment. Formed before weighing the candidate's own score.
