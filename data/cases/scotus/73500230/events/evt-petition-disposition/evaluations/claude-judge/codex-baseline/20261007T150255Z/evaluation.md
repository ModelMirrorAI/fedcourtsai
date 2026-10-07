# Evaluation of codex-baseline — Wealthy, Inc. v. Cornelia, No. 25-1329 (evt-petition-disposition)

## Outcome and scores

The event is a **cert** cell (`event.yaml` `stage: cert`, moment `distribution`). The petition was **denied** on the October 5, 2026 order list after a single conference (the 9/28 long conference; the outcome's `distribution_count` is 1), with no noted dissent or statement. `actual_granted` = 0.

- `correct` = 1: predicted `denied`, actual `denied`.
- `brier_score` = (0.14 − 0)² = **0.0196**.
- `segment_base_rate` = **0.0512** on the `risk_set` basis. The prediction froze `band: baseline` under `salience_version: sal-v4`, Term 2025; the statpack band table's heading is sal-v4, so the version resolves. Pooling the bracketed `reached` baseline figures weighted by `n` over every rendered Term strictly before OT2025 (OT2017–OT2024, eight rows; the caption says 10 of 10 Terms are rendered, so the rendered window and the configured lookback coincide on the available rows) gives 5.12% over a weighted n of 11,580, from the table's rounded percentages. This is the same figure the candidate itself computed.
- `brier_skill_score` = 1 − 0.0196 / 0.0512² = **−6.48**. Negative because 0.14 sits well above the 5.1% baseline on a denial; between the other two candidates in magnitude.

The claims block is scored by the harness and not here; the forecast document was read only for context.

## Reasoning quality: 0.78

What drove the score up:

- **The anchor is exactly right and transparently derived**: the sal-v4 baseline risk-set figures for OT2017–OT2024, denominator-weighted, 5.12% over n 11,580, with the caveat that the pooling uses rounded published percentages. It also correctly explains why the terminal (leading) figures and the mixed-court cuts are the wrong population.
- **It read the late filings** (brief in opposition Aug 26, reply Sep 11) from the snapshot's own links, logged exactly which pages, and used them: preservation, independent Rule 56 grounds, unfinished fee proceedings, the nonprecedential decision, and the fact-bound character of Question 2 all come from the record rather than from speculation.
- **Careful epistemics.** It labels the vehicle objections "advocacy-supported risks, not adjudicated forfeiture", says plainly what would move the number in each direction, and separates the base rate's committed-pack status from any live-corpus claim. It also correctly refuses to read the duplicate distribution notice as a relist.

What held it back:

- **It set aside the strongest case-specific signal.** The brief in opposition it read reports the Court's June 15, 2026 denial in Gopher Media, a Ninth Circuit anti-SLAPP petition, and the document explicitly declines to treat that denial as "dispositive negative precedent" because the reply distinguishes it. The reply's distinction (immediate appealability versus applicability) is real, but the relevant inference is not about doctrine; it is that the Court passed on the same statute-in-federal-court controversy from the same circuit three months earlier without a relist, and has done so repeatedly. claude-baseline drew that inference and landed much closer to the outcome; this document left the lift from the response request largely uncorrected, and 0.14 is the result.
- **The response-request lift is unsized.** The document says the July request "demonstrates attention" but never says how much it moves a baseline paid petition, so the step from ~5% to 14% is stated rather than argued.
- A substantial share of the document narrates tool limitations (browser, pdftotext, uv cache) rather than the case; useful for a maintainer, neutral for the analysis.

## Leakage

Mode `forward`; the prediction was created September 17, 2026 and the petition was decided October 5, 2026, so the case was genuinely open. The log (coverage 0.90) shows HTTP fetches of the brief in opposition and the reply via the exact supremecourt.gov links in the snapshot, plus provisioned-file and statpack reads; the three `unobserved` browser rows are graded on their URLs, which name those same two pre-decision filings. No corpus query, no MCP call, no query for this petition's result, no `data/qp-topics/` read, and `retrieval.md` states that no disposition was sought or seen. `retrieved_outcome_material` = false, `influenced_prediction` = not_applicable, `leakage_suspected` = false. Not a mis-provisioned decided case. The candidate's `flags.json` is not staged, so nothing is inferred from its absence.

## Big-case read

My independent read is 0.35 (see `evaluation.json`): an important, recurring procedural question carried by a small, low-profile vehicle that was denied without comment.
