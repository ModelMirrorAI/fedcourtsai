# Evaluation of codex-baseline — scotus/73281703, evt-petition-disposition

**Stage:** cert (event.yaml `stage: cert`). **Outcome:** petition denied 2026-10-05 after the 2026-09-28 conference, `actual_granted` 0, no noted dissent, two distributions, no CVSG.

## Scores

| field | value |
| --- | --- |
| predicted_disposition | denied (matches) → `correct` 1 |
| probability | 0.36 → `brier_score` 0.1296 |
| segment_base_rate | 0.1724 (`risk_set`) |
| brier_skill_score | −3.360 |
| reasoning_quality | 0.62 |

**Base rate.** The prediction froze `band: elevated` under `salience_version: sal-v4`, matching the statpack table heading, so the basis is `risk_set`. Pooling the bracketed `reached` figure for `elevated` over Terms 2017–2024 (every rendered Term strictly before Term 2025; the caption says 10 of 10 pack Terms are rendered, so there is no window divergence) gives weighted n 2810 and rate 0.1724 — the same 17.24% the candidate itself computed. The baseline Brier is 0.0297; a 0.36 forecast against a denial is more than four times worse, hence the strongly negative skill.

## What the prediction got right

The categorical call was right and the modal path it described — no further distribution, denial after the September 28 conference, no separate writing — is exactly what happened. The candidate pooled the anchor correctly and by the right method, treated the second distribution as administrative rather than a substantive relist, and verified two of the petition's authorities (Flynn, Redd) on CourtListener rather than taking the briefs' word. Its account of the brief in opposition is accurate: the retaliation-versus-discrimination mismatch, the staffing-agency employment, the antecedent private-retaliation-action question, and the unchallenged dispositions of the ACRA and section 1983 claims are all what the opposition argues.

## Where the reasoning is weaker

The analysis identified every reason denial should lead and then more than doubled the anchor anyway, to 0.36, on the strength of a conceded split, a response request, and expert counsel. The candidate itself calls the adjustment "judgment, not a fitted coefficient," and the outcome shows it was too large: a petition with an acknowledged QP-to-record mismatch, no amici, and a small general verdict from a state court was denied at its first conference with no relist and no writing. Two specific points. First, the response request is treated as a "real attention signal" on top of a band that already encodes it; the candidate notes the double-counting risk but does not discount for it. Second, the Redd point — that Redd "allows further consideration" of retaliation claims by a non-employee — is used to weaken the opposition's distinction, but Redd involved a federally conducted program and the plaintiff's own exclusion, as the candidate concedes, so it carries little weight on the question whether a non-disabled advocate's retaliation claim fits the stated question. The candidate also did not read the reply, which it discloses. The process is careful and honest; the calibration is what costs it, so `reasoning_quality` is 0.62 — above gemini-baseline for depth and accuracy of characterization, below claude-baseline for weighing.

## Leakage

Forward cell; `influenced_prediction` is `not_applicable`, `retrieved_outcome_material` false, `leakage_suspected` false. Prediction created 2026-09-18, before the conference and the denial. Of 33 logged calls, 31 are captured; the two `unobserved` rows are hosted web searches whose queries name a 2016 Fifth Circuit opinion (Flynn, 15-50314) and Supreme Court Rule 10, not this case, so they are graded on their queries as clean. The CourtListener calls fetch historical authorities only (812 F.3d 422; Redd v. Summers, 2000). No call names this petition's docket, caption, or disposition, and no `retrieved_doc_date` falls on or after 2026-10-05. The reasoning states explicitly that no disposition was retrieved.

## Big case

My independent read, formed before looking at the candidate's score: 0.30 — a real inter-court division on section 504's reach to non-employees, but a weak vehicle and a plain denial. The candidate's 0.44 is recorded in its prediction; I supply only my read.

## Harness fields

`claim_scores`, `process_version`, `base_rate_salience_version`, and `prediction_run_id` are left to the harness. `vote_accuracy` and `judgment_correct` are omitted/null on this cert cell. No `semantic_grades` block: a cert event declares no semantic set.
