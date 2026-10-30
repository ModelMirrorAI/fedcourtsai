# Retrieval record

## Baseline and local context

Read the supplied event, case-level October 2, 2026 snapshot, context, document manifest, questions presented, and relevant petition/appendix passages. Read the committed `metrics/statpack.md` and `metrics/statpack.json`; calculated the sal-v4 state-band reached rate across 2017–2025 from the JSON: 104 / 426 = 0.2441314554. These committed artifacts supplied no corpus-wide pull/snapshot vintage. No other cell's prediction or evaluation and no question-topic measurement artifact was consulted.

## Corpus tooling calls

1. `uv run fedcourts paths --court scotus --docket 9026000176 --event evt-order-call-for-response-disposition --role predictor` — first attempt failed because the default uv cache was read-only. Repeated with a writable temporary uv cache; returned the case, corpus, and event paths, without exposing the evaluator-only outcome.
2. `uv run fedcourts query --help` — first attempt had the same cache error. Repeated successfully with the temporary cache. A subsequent help-only call with wider terminal formatting inspected the option list. Help calls made no prior retrieval.
3. `uv run fedcourts query --court scotus --disposition summary-reversal --decided-before 2026 --limit 3` — completed successfully, with no matching rows. The prior-Term bound was used conservatively even though this cell is forward mode. Its empty sparse-label result was not used as a frequency estimate or an inference about this case. Stderr reported:

   `ranged corpus reads: 902 GET(s), 236060672 byte(s)`

No `--full` opinion hydration or own-case corpus lookup was performed.

## CourtListener MCP

One `search` call, `type="o"`, `citation="421 U.S. 482"`, `num_results=2`, sought the preexisting Pitchess opinion. It failed with HTTP 429: daily limit 1400/day, expected availability in 5569 seconds. No opinion was returned. No direct CourtListener REST request, credential extraction, or retry was attempted.

## Web attempts

One search call contained both queries:

- `Pitchess v Davis 421 U.S. 482 1975 retrial conditional writ supervision exhaustion`
- `Gentry v Deuth 456 F.3d 687 conditional writ jurisdiction retrial`

The web tool supplied no usable visible result. One subsequent `open` attempted the GovInfo U.S. Reports PDF for Pitchess, volume 421, page 482; it likewise supplied no usable visible content. No external legal proposition is treated as independently verified by those attempts. Neither search targeted the current petition, its disposition, or its subsequent history.

## Scope

The forecast uses the provisioned predecision record and committed base rates. The prior petition's denial discussed in the provisioned July petition is historical input, not the predicted outcome. No current-case disposition was sought or encountered.
