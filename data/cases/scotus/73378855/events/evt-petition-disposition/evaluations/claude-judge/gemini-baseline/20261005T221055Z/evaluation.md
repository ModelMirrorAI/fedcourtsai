# Evaluation of gemini-baseline — scotus/73378855, evt-petition-disposition

**Outcome.** Petition denied on the 2026-10-05 order list after one distribution (conference of 2026-09-28), no noted dissent. Cert-stage cell, forward mode.

**Scores.** `predicted_disposition` = `denied` matches → `correct` = 1. P(grant) = 0.01 against `actual_granted` = 0 → Brier 0.0001. Frozen `band` = `baseline`, `salience_version` = `sal-v4`, matching the statpack heading, so `base_rate_basis` = `risk_set`: pooled bracketed `reached` `baseline` rate over rendered Terms 2017–2024 = 593 / 11,580 = 0.05121; baseline Brier 0.002622; skill = 0.962. The candidate's "approximately 5.1%" anchor is the right figure from the right rows.

**What it got right.** The anchor is correct and the central vehicle point is the right one: a no-opinion affirmance from the Supreme Court of Alabama leaves the Court nothing to review, and the questions presented recast settled Gore / State Farm / Cooper Industries doctrine rather than raising a split. The prediction's number landed where the two more thorough candidates landed.

**Weaknesses.** The rationale is a single paragraph and, by its own account, rests on the snapshot and `questions-presented.txt` only. It did not read the petition or the brief in opposition, so it misses everything that actually drives this petition to the floor of the band: the pro se, disbarred-lawyer petitioner; the remittitur-hearing transcript showing the trial judge addressed the guideposts orally; the 2.2:1 ratio; TXO's rejection of an articulation requirement; the absence of any BIO from the judgment creditor. The claim that the no-opinion posture makes it "nearly impossible" to assess the lower court's reasoning is right in direction but overstated, since the Court can and occasionally does review silent state affirmances where the federal question is clear. The number is well-calibrated, but the document does not show the work that justifies it; a reader cannot tell whether 0.01 was reasoned or defaulted.

**Reasoning quality: 0.45.** Correct anchor and correct headline point, but a thin analysis that engaged with a third of the provisioned record and would have produced the same paragraph for most baseline-band petitions.

**Leakage.** Forward cell. Prediction created 2026-09-17 against the 2026-09-16 snapshot; denial came 2026-10-05, so no outcome existed to retrieve. Log of 25 calls, every marker `unobserved` (coverage 0.0, an engine's standing telemetry shape, not a defect), so each call is graded on its query: provisioned file reads, directory listings, a statpack read, output writes, and a validate run. No web, corpus, or MCP call; nothing names this docket's disposition. `retrieved_outcome_material` = false, `influenced_prediction` = not_applicable, `leakage_suspected` = false.

**Big case.** My independent read is 0.05 (see claude-baseline's write-up for the basis).
