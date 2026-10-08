# Evaluation of gemini-baseline — Wealthy, Inc. v. Cornelia, No. 25-1329 (evt-petition-disposition)

## Outcome and scores

The event is a **cert** cell (`event.yaml` `stage: cert`, moment `distribution`). The petition was **denied** on the October 5, 2026 order list after a single conference (the 9/28 long conference; the outcome's `distribution_count` is 1), with no noted dissent or statement. `actual_granted` = 0.

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.35 − 0)² = **0.1225**.
- `segment_base_rate` = **0.0512** on the `risk_set` basis. The prediction froze `band: baseline` under `salience_version: sal-v4`, Term 2025; the statpack band table's heading is sal-v4, so the version resolves. Pooling the bracketed `reached` baseline figures weighted by `n` over every rendered Term strictly before OT2025 (OT2017–OT2024, eight rows; the caption says 10 of 10 Terms are rendered, so the rendered window and the configured lookback coincide on the available rows) gives 5.12% over a weighted n of 11,580, from the table's rounded percentages.
- `brier_skill_score` = 1 − 0.1225 / 0.0512² = **−45.7**. A probability of 0.35 against a 5.1% baseline on a denial is roughly forty-seven times the baseline's squared error; this is the weakest of the three cells by a large margin.

The claims block is scored by the harness and not here; the forecast document was read only for context.

## Reasoning quality: 0.35

The document is a single paragraph. What it gets right:

- It correctly characterises Question 1 as a genuine, multi-way circuit split under Shady Grove, correctly reads the docket (initial waiver, response requested July 27, one amicus, distributed for the long conference), and correctly notes that vehicle problems are the main uncertainty. Its forecast that only QP 1 would be taken if anything were is sound.
- It names the right table (the sal-v4 baseline bracketed reached figure) as its anchor.

What pulled the score down:

- **Wrong anchor row.** The "~3.9% bracketed reached rate" it quotes is the OT2025 row, the case's own Term, which the predict contract excludes; the strictly-prior pool is about 5.1%. The direction of the error happens to be harmless here, but it is the one anchoring rule the cell is held to and the document misapplied it.
- **No engagement with the Court's track record on this exact question.** The brief in opposition (filed Aug 26, linked in the snapshot) reports a string of anti-SLAPP denials, including one from the same circuit three months earlier after one conference. The document admits it did not read the BIO and relied on "the general reluctance of the Court to grant cert in every split". Both other candidates fetched the filing; this one did not, and its number is the one that suffered for it.
- **An unsized, very large lift.** It moves from a ~4–5% floor to 0.35, nearly a nine-fold increase, on a response request plus "the entrenched nature of the split", with no analogue, no cut, and no estimate of how often a called-for response ends in a grant for a paid baseline petition. The statpack carries no conditional rate for a call for response, so the lift was always going to be judgment, but a judgment this large needs an argument, and none is given.
- **A mistaken mechanism in the forecast.** It expects a relist because "the Court often relists cases with a requested response to give the Justices time to review the newly filed brief in opposition." A response request delays the first conference; it does not generate relists. The forecast document is not scored, but the same misunderstanding of the docket mechanics informs the headline number.
- The vehicle discussion is speculative ("could present vehicle issues, e.g. if the state-law standard wouldn't change the outcome") rather than drawn from the record, and it does not mention the preservation problem, the unpublished disposition, or the interlocutory posture that the filings put squarely in play.

In short, the right label for the wrong reasons at the wrong confidence.

## Leakage

Mode `forward`; the prediction was created September 17, 2026 and the petition was decided October 5, 2026, so the case was genuinely open. The log's `result_capture_coverage` is 0.0: every marker-carrying call is `unobserved`, which is this engine's standing telemetry shape and not a defect, so each call is graded on its query. The queries are provisioned-file reads, statpack greps, and two corpus queries (an "anti-SLAPP federal court Shady Grove" search bounded `--decided-before 2026-09-17`, and a bare `--decided-before 2026` slice). No web fetch, no MCP call, no query for this petition's disposition, no `data/qp-topics/` read; the reasoning reads the docket as distributed once with a response requested. `retrieved_outcome_material` = false, `influenced_prediction` = not_applicable, `leakage_suspected` = false. Not a mis-provisioned decided case. The candidate's `flags.json` is not staged, so nothing is inferred from its absence.

## Big-case read

My independent read is 0.35 (see `evaluation.json`): an important, recurring procedural question carried by a small, low-profile vehicle that was denied without comment.
