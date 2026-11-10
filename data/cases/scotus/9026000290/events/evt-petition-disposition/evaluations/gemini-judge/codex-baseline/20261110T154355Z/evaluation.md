# Evaluation of `codex-baseline` — `scotus/9026000290` (`evt-petition-disposition`)

## 1. Outcome and Quantitative Summary

- **Stage:** `cert` (`kind: petition`, `moment: distribution`)
- **Actual Outcome (`outcome.json`):** `actual_disposition: "denied"`, `actual_granted: 0`, `disposition_basis: "standard"`, `disposition_route: null`, `noted_dissent_from_denial: false`, `resolved_at: "2026-11-09"`, `signals: {"cvsg_date": null, "distribution_count": 1, "distribution_parse": "dist-v2"}`.
- **Candidate Forecast (`prediction.json`):** `granted: 0`, `predicted_disposition: "denied"`, `probability: 0.004`, `big_case_score: 0.22`.
- **Scored Metrics:**
  - `correct`: `1` (exact disposition label match: `"denied" == "denied"`)
  - `brier_score`: `0.000016` (`(0.004 - 0)^2`)
  - Segment base rate, Brier skill score, and declared `claim_scores` are computed and stamped by the harness against the stamped segment base rate.

## 2. Reasoning Quality (`reasoning_quality`: `0.91`)

`codex-baseline` delivered a rigorous, well-calibrated analysis in `reasoning.md`:

- **Base-rate anchoring (graded against statpack build `eb6830084a18` via `fedcourts statpack-at`):** `codex-baseline` properly anchored on the `sal-v4` `baseline` band's risk-set (`reached`) rate across strictly prior Terms (`OT 2017`–`OT 2025`) from the statpack build in force when it ran on October 22, 2026. It clearly explained why the private-petitioner `baseline` risk set governs even though the Superior Court of California is named as the nominal respondent in a writ caption, and properly distinguished terminal cuts (`relist_bucket = 0`, `cvsg = none`) from forward transition probabilities at the first distribution moment.
- **Record grounding:** `codex-baseline` carefully inspected the docket snapshot (`2026-10-22.json`), `documents.json`, `questions-presented.txt`, and `petition.txt` (including the appendices). It accurately identified that the California Supreme Court (`S295215`) and First Appellate District (`A175551`) orders were summary denials of review and extraordinary writ/stay relief arising from an August 27, 2025 San Francisco Superior Court order sustaining a demurrer to a seventh amended complaint with and without leave to amend, and noted that the substantive trial-court reasoning was omitted from the appendix in favor of a Clerk's Office notice. Unlike `gemini-baseline`, however, `codex-baseline` did not use the CourtListener MCP server to retrieve the referenced federal district court orders (`Emberton v. San Francisco City Government`, N.D. Cal. No. `3:22-cv-05440-TSH`), which were available on RECAP and detailed the underlying municipal code-enforcement dispute.
- **Consideration balance & calibration justification:** Even while justifying a very low grant probability (`0.004`), `codex-baseline` articulated why the probability remained strictly positive (residential Fourth Amendment privacy and municipal code inspections are genuine federal constitutional subjects, and an omitted trial-court order in the appendix should not be over-read as affirmative proof of how the merits were resolved below) before weighing the decisive factors pulling toward denial (no genuine split among federal circuits or state high courts, interlocutory writ/demurrer posture raising 28 U.S.C. § 1257(a) finality obstacles, diffuse multi-claim framing, and distribution after the October 5, 2026 response deadline passed without a BIO or CFR).

## 3. Predicted reasoning (`predicted_reasoning_quality`: `0.85`)

`codex-baseline`'s `predicted_reasoning.md` was specific and borne out on every unconditional claim that the November 9, 2026 disposition tested:

1. **Unexplained denial on the post-November 6 conference order list (`borne-out`):** Correctly forecast that the Court would deny the petition without explanation on the order list immediately following the November 6, 2026 conference (`actual_disposition: "denied"`, `disposition_basis: "standard"`, `resolved_at: "2026-11-09"`).
2. **Single-distribution resolution with no relist or CFR (`borne-out`):** Correctly forecast that the petition would resolve on its initial distribution (`distribution_count: 1`) without a relist or call for a response.
3. **No CVSG (`borne-out`):** Correctly forecast that the Court would not invite the Solicitor General's views (`cvsg_date: null`).
4. **No dissent or statement respecting denial (`borne-out`):** Correctly forecast that no Justice would note a dissent or write separately (`noted_dissent_from_denial: false`, `votes: []`).
5. **Conditional grant scope and route (`unresolved`):** Its counterfactual analysis of how the Court would narrow the question presented and weigh a summary GVR (`0.35`) versus plenary review was well-reasoned but untested by the denial.

## 4. Leakage and Big-Case Assessment

- **Leakage (`leakage_suspected`: `false`, `influenced_prediction`: `"not_applicable"`):** Forward prediction created on `2026-10-22T10:30:40Z`, 18 days before the `2026-11-09` conference order list. The captured `retrieval_log.json` (local file reads and shell commands only) and reasoning confirm that the case was unresolved when predicted.
- **Big-case read (`evaluator_score`: `0.03`):** Routine pro se petition arising from an interlocutory state-court demurrer in a localized residential fence and code-enforcement dispute, with no split of authority, no amicus filings, and no broader doctrinal impact. (`codex-baseline`'s `big_case_score` of `0.22` was somewhat generous for this vehicle.)
