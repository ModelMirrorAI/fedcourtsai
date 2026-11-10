# Evaluation of `claude-baseline` — `scotus/9026000290` (`evt-petition-disposition`)

## 1. Outcome and Quantitative Summary

- **Stage:** `cert` (`kind: petition`, `moment: distribution`)
- **Actual Outcome (`outcome.json`):** `actual_disposition: "denied"`, `actual_granted: 0`, `disposition_basis: "standard"`, `disposition_route: null`, `noted_dissent_from_denial: false`, `resolved_at: "2026-11-09"`, `signals: {"cvsg_date": null, "distribution_count": 1, "distribution_parse": "dist-v2"}`.
- **Candidate Forecast (`prediction.json`):** `granted: 0`, `predicted_disposition: "denied"`, `probability: 0.004`, `big_case_score: 0.03`.
- **Scored Metrics:**
  - `correct`: `1` (exact disposition label match: `"denied" == "denied"`)
  - `brier_score`: `0.000016` (`(0.004 - 0)^2`)
  - Segment base rate, Brier skill score, and declared `claim_scores` are computed and stamped by the harness against the stamped segment base rate.

## 2. Reasoning Quality (`reasoning_quality`: `0.81`)

`claude-baseline` produced a sensible, well-calibrated probability (`0.004`), though its investigation and write-up were shallower than `codex-baseline`'s and `gemini-baseline`'s:

- **Base-rate anchoring (graded against statpack build `eb6830084a18` via `fedcourts statpack-at`):** `claude-baseline` consulted the `sal-v4` salience-band table in the statpack build in force when it ran on October 22, 2026, identifying the prior-Term `baseline` reached-rate range and approximate pooled anchor before applying four downward adjustments. Unlike `codex-baseline` and `gemini-baseline`, it used an approximate pooled figure rather than summing the prior-Term denominators, and its remark that the `relist-0` cut "describes petitions that *ended* undistributed" slightly misstates `relist_bucket = 0` (which covers petitions distributed once that ended *unrelisted*), though it correctly recognized that `relist_bucket = 0` is a terminal cut that understates the forward risk set at first distribution.
- **Record grounding:** `claude-baseline` accurately identified the pro se paid posture, the California Supreme Court denial of review (`S295215`) of the First Appellate District's summary denial (`A175551`) of a writ petition arising from a San Francisco Superior Court demurrer to a seventh amended complaint (`CGC-22-601288`), the petitioner's attempt to pit two lines of Supreme Court precedent (*Ciraolo*/*Dow*/*Barlow's* vs. *Katz*/*Kyllo*) against one another rather than showing a lower-court split, the commingled RICO/§§ 1981/1983/1985/18 U.S.C. § 242/ethics claims, and the passed October 5, 2026 response deadline. However, `retrieval_log.json` shows that `claude-baseline` read only lines 1–400 of `petition.txt` (leaving the remaining 1,300+ lines and appendices unread) and did not use CourtListener MCP to inspect the referenced N.D. Cal. docket (`22-cv-05440-TSH`).
- **Consideration balance & calibration justification:** `claude-baseline` concisely justified why the petition belongs at the probability floor (`0.004`) while keeping `P(grant)` above zero for tail risk and noting a small residual chance (`0.03`) of an administrative reschedule or hold.

## 3. Predicted reasoning (`predicted_reasoning_quality`: `0.80`)

`claude-baseline`'s `predicted_reasoning.md` was concise and borne out on all four central claims tested by the November 9, 2026 order list:

1. **Plain unexplained order-list denial from the November 6, 2026 conference (`borne-out`):** Correctly forecast that the petition would be denied at the November 6, 2026 conference by a plain order-list entry with no explanation (`actual_disposition: "denied"`, `disposition_basis: "standard"`, `resolved_at: "2026-11-09"`).
2. **No relist and no call for a response (`borne-out`):** Correctly forecast that the petition would not be relisted (`distribution_count: 1`) and that no BIO would be requested.
3. **No CVSG (`borne-out`):** Correctly forecast that no CVSG would issue (`cvsg_date: null`).
4. **No separate writing (`borne-out`):** Correctly forecast no dissent from denial and no statement respecting it (`noted_dissent_from_denial: false`, `votes: []`).

## 4. Leakage and Big-Case Assessment

- **Leakage (`leakage_suspected`: `false`, `influenced_prediction`: `"not_applicable"`):** Forward prediction created on `2026-10-22T10:28:41Z`, 18 days before the `2026-11-09` conference order list. The captured `retrieval_log.json` (local file reads and shell commands only) and reasoning confirm the case was genuinely open when predicted.
- **Big-case read (`evaluator_score`: `0.03`):** Routine pro se petition arising from an interlocutory state-court demurrer in a localized residential fence and code-enforcement dispute, with no split of authority, no amicus filings, and no broader doctrinal impact. (`claude-baseline`'s `big_case_score` of `0.03` matched this assessment.)
