# Evaluation of codex-baseline — scotus/73300246, evt-petition-disposition

## Outcome and scoring

Cert cell (`event.yaml` stage `cert`). The petition in No. 25-1254, Harvey v. City of Reno, was distributed once (June 24 for the September 28, 2026 conference) and **denied on October 5, 2026** with no noted dissent and no CVSG (`outcome.json`: `actual_disposition: denied`, `actual_granted: 0`, `distribution_count: 1`).

- `predicted_disposition: denied` → **correct = 1**.
- `probability: 0.025` → **brier_score = 0.000625**.
- **segment_base_rate = 0.0512**, basis **`risk_set`**. The prediction's frozen context carries `band: baseline` with `salience_version: sal-v4`, matching the statpack's sal-v4 band table heading. Pooled bracketed `reached` figure for `baseline`, weighted by `n`, over the rendered Terms strictly before OT2025 (OT2017–OT2024): 5.12% over n = 11,580. The caption says "Most recent 10 of 10 Term(s)", so the rendered window is the pack's whole window; no divergence to flag.
- **brier_skill_score = 0.7616** (1 − 0.000625 / 0.0512²). Lower than the two candidates at 0.015 purely because the number sat higher; still a large margin over the baseline.
- No `vote_accuracy` (cert stage). No `semantic_grades` (cert cell). `claim_scores` and `process_version` are the harness's.

## Reasoning quality: 0.84

A rigorous, carefully hedged rationale whose legal analysis is the deepest of the three on the record itself:

- **Anchor derived exactly right, with the right caveats.** It pools the bracketed `reached` baseline rate over OT2017–OT2024 to 5.12% over 11,580 — identical to my scoring baseline — and explicitly refuses the terminal zero-relist and CVSG cuts as forward hazards ("describe shape only"). That is the correct reading of the statpack and the point on which gemini-baseline stumbled.
- **It read the Nevada affirmance, not just the briefs.** It cites the appendix for the rejection of easement by necessity (no common ownership), prescription (not against the State), and implied easement; separates the inverse-condemnation ruling on the access claim (no interest) from the ruling on the 1987 excess-taking theory (pleading and limitations); and finds the footnote holding the NRS 408.533 argument waived below. Those are the actual obstacles, and the preservation point is one neither other candidate found.
- **Disciplined about advocacy.** It declines to adopt the BIO's broad "everything is time-barred" framing, distinguishes the two takings theories, treats the asserted conflict as advocacy rather than a split pending its own verification, and refuses to resolve the landlocked-or-not factual dispute on briefs alone — while correctly noting that the dispute itself is what makes the vehicle unattractive.
- **Checked the one precedent it leaned on.** The Tyler v. Hennepin County proposition was verified through CourtListener and scoped narrowly ("does not itself establish a compensable easement or complete loss of access here").
- **Candid about limits.** Petition truncation, unread reply, failed web calls, and the absence of a quantified model behind the discount are all stated.

Where it is a notch below claude-baseline: it gives the federal theory somewhat more credit ("a real federal theory, not a nonexistent issue") than the Court's unexplained denial and the petition's own concessions warranted, which is what left the number at 0.025 rather than lower; and it attends less to the case-selection profile outside the merits (unpublished state-court origin, the originating-court pattern, waiver by three respondents, no amici, solo counsel), which are strong and cheap signals on a petition like this. The length also carries some material not relevant to the disposition grade (the summary-route and relist hazards). These are differences of emphasis, not errors.

## Leakage: not applicable (forward)

Mode is `forward` in both the log and the frozen context; the prediction was created 2026-09-16, before the conference and the denial. 27 calls, 25 captured; the two `unobserved` rows are hosted web calls — a general search on Tyler v. Hennepin County and an attempt to open the Tyler slip opinion — graded on their queries, neither of which names this petition. The two CourtListener lookups resolve the Tyler citation and search inside that opinion for "traditional property interests"; both are disclosed in `retrieval.md` as precedent checks. No query names this docket, caption, or disposition; no `retrieved_doc_date`; no read of `data/qp-topics/` (the candidate's note that it inspected `metrics/statpack.json` top-level keys is a statpack read, not a topic-label read). `retrieved_outcome_material = false`, `influenced_prediction = not_applicable`, `leakage_suspected = false`.

## Big case

My independent read is 0.10: a fact-bound, local access dispute from an unpublished state order, denied without comment. Formed before weighing the candidate's own score.
