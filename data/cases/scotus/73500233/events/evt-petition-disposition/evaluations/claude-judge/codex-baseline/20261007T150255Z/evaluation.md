# Evaluation: codex-baseline

**Outcome.** Cert denied on the October 5, 2026 order list after the September 28 long conference, with one distribution, no call for a response, no CVSG, and no noted dissent. The event stage is `cert`.

**Scores.** `predicted_disposition` = `denied` matches `actual_disposition`, so `correct` = 1. P(grant) = 0.01 against `actual_granted` = 0 gives a Brier of 0.0001.

**Baseline.** The prediction's frozen context carries `band` = `baseline` and `salience_version` = `sal-v4`, and the committed statpack's "Segment base rate by salience band" heading names sal-v4, so the basis is `risk_set`. I pooled the bracketed `reached` figure for `baseline`, resolved-weighted, over the rendered Terms strictly before Term 2025 (2017 through 2024, eight Terms; the caption says it renders 10 of 10 Terms, so the rendered window is the pack's whole window and the in-code ten-Term lookback reaches no row this table does not show): about 593 weighted grants over n = 11,580, a rate of 0.0512. Brier skill = 1 - 0.0001 / 0.0512^2 = 0.962.

**What the reasoning got right.** This is a careful rationale. It names the right anchor and computes it from the right rows (same 5.12% I reach), then gives four grounded reasons to discount to 1%: the petition's own concession that no authority approves or disapproves the practice (so no split), the vehicle problems visible in the petition (unpublished per curiam below, trial counsel's agreement to admission, an ineffective-assistance route), the doctrinal headwind from Dowling v. United States, which it actually retrieved and read rather than recalled, and the thin institutional signal (waiver, single distribution). Each is tied to a page of the petition. It is also honest about what it did not have (no appendix, no lower-court opinion, no BIO) and that its account of the lower courts comes from the petitioner's advocacy. The outcome bore all of it out.

**What I would mark down.** Little. The relist-increment and summary-route numbers are stated as judgments without much derivation, and the discussion of Villarreal is slightly hedged in a way that reads as uncertainty about what the case holds rather than analysis of it. Neither affects the headline number or its justification. The reasoning quality here grades the soundness of the analysis, not the forecast document, which I read for context only.

**Reasoning quality: 0.85.**

**Leakage.** Forward cell. The 28-call log shows reads of the provisioned record, statpack and prompt, two unobserved web-search rows whose queries name Villarreal and the Cornell page for 493 U.S. 342, and CourtListener lookups that resolved to the 1990 Dowling majority. No call targets this docket's disposition and no `retrieved_doc_date` is at or after October 5, 2026; the prediction predates the conference. `retrieved_outcome_material` = false, `influenced_prediction` = `not_applicable`, `leakage_suspected` = false. The retrieval note matches the log.

**Big case.** My own read, formed before looking at the candidate's score: 0.10. A single state criminal defendant's evidentiary objection, unpublished per curiam below, no split alleged, respondent waived, no amici, denied without a word. The candidate's 0.38 weighs the hypothetical nationwide reach of the rule it asks for; I weigh the vehicle and the attention it drew. No agreement number is computed here.
