# Evaluation of codex-baseline — scotus/9526000447, evt-motion-disposition

## The cell

This is an **interim** cell (`event.yaml` stage `interim`): Swift Transportation's emergency application 26A447 to stay a New Mexico trial court's discovery-examiner order pending a certiorari petition, submitted to Justice Gorsuch on September 30, 2026. `outcome.json` records `actual_disposition: denied`, `actual_granted: 0`, resolved 2026-10-02, with `interim_signals` of no response requested, no referral to the Court, and zero amicus briefs. The 2026-10-03 snapshot carries the disposing entry: "Application (26A447) denied by Justice Gorsuch", October 2, 2026, two days after submission.

## Scores

- `correct` = 1: the candidate predicted `denied`; the outcome is `denied`.
- `brier_score` = (0.06 − 0)² = 0.0036.
- `segment_base_rate` and `brier_skill_score` are **not written here**: on an interim cell the harness pools the baseline from the committed statpack's interim section over application-Terms strictly before the prediction's own (Term 2026, so 2016–2025) and derives the skill from it at the stamp; `base_rate_basis` stays null because an application freezes no band. For the reader: the committed pack's rendered rows for that window are Term 2025 (17 granted of 226 resolved substantive) and Term 2024 (14 of 70; 972 of that Term's applications unparsed), pooled 31/296 ≈ 10.5%, above the 50-resolved floor, so I expect a non-null stamp. If it comes back null, the pack could not support the pool rather than the section being absent. The prediction's `context.band` is null, the ordinary interim shape, so no cert-band flag.
- `vote_accuracy`, `judgment_correct`, `semantic_grades`: omitted or null. Not a merits cell; the prediction's `semantic_claims` is null, as expected on an interim event.
- `claim_scores`: the harness's; not written.

## Reasoning quality: 0.80

Graded on `reasoning.md` only. The candidate correctly identified the information set (arrival-position cut at index zero, forward mode, the September 30 submission as the arrival moment rather than the October 2 docketing header) and correctly computed the eligible pool (31/296 over application-Terms 2016–2025, independently summed from the pack's JSON), with a careful account of what the pool is and is not: uneven coverage, machine-matched resolutions only, denial-first on mixed orders, and the escalation-ladder selection that makes the scored population sit above the pooled one. That last point is the sharpest methodological observation either candidate made.

The substantive analysis is sound and, unusually, two-sided: it read the state-court opposition in the appendix and used it to discount the application's "general warrant" framing without adopting the respondents' account as fact. It verified the stay standard (Hollingsworth) and the finality authority (Fisher) through CourtListener and read Fisher's footnote narrowly, correctly treating finality as a live weakness rather than a categorical bar. It also picked up the application's footnote on plaintiffs' proposal to defer sanctions and drew the right inference about imminence.

Two things hold it slightly below claude-baseline. First, the adjustment from 10.5% to 6% leans on "compelled disclosure cannot readily be undone", which is the irreparable-harm prong, when the posture facts it had already identified (private civil litigant, interlocutory state discovery order, no split) go to the reasonable-probability-of-certiorari prong that a Circuit Justice reaches first; the candidate named that prong as decisive in one sentence but let the harm prong keep its number higher than its own analysis supports. Second, the increment probabilities are labelled "judgmental" and left there, with less tying them to the published counts than the disposition number got. Neither is an error of law or of reading.

## Leakage

Forward cell (`retrieval_log.json` mode `forward`, capture coverage 0.93). The two uncaptured rows are web searches graded on their queries: a Hollingsworth v. Perry citation query and a Library of Congress U.S. Reports PDF URL for Fisher v. District Court, both precedent lookups naming no party or docket in this case. The captured CourtListener calls are opinion searches for 558 U.S. 183 and Fisher (1976) plus two in-document snippet searches. No shell call, search, or MCP call names this docket, 26A447, or Swift. The prediction was created at 2026-10-02T21:30Z and the event resolved on 2026-10-02, so the denial may have been public when the cell ran, but nothing in the log or the reasoning shows it reaching the candidate, and `reasoning.md` states the outcome was unknown and that the passing of the October 1 hearing date was not read as evidence of anything. `retrieved_outcome_material` = false, `influenced_prediction` = `not_applicable`, `leakage_suspected` = false. The candidate's `flags.json` is not staged, so its disclosure channel was only its prose.

## Big case

My independent read is 0.12: a one-case discovery-sanctions fight between private parties, a novel theory with no uptake anywhere, and a two-day single-Justice denial with no response, referral, amicus, or dissent. One honesty note: the predictor's `big_case_score` sits in the staged `prediction.json` I read before forming this, so I cannot claim a strictly unanchored read; I formed the number from the record and the outcome and did not adjust it toward theirs.
