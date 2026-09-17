# Retrieval record

## Committed context

- Read metrics/statpack.md: modern discretionary-cert disposition table, paid-segment relist and CVSG cuts, and sal-v4 salience-band table.
- Read relevant fields in metrics/statpack.json. Pooled the elevated band's prefix estimates across displayed Terms 2017–2024, strictly before the cell's Term 2025: 484 / 2810 = 0.17224199288256228.
- Checked the statpack's last commit timestamp with `git log -1 --format='%h %cI' -- metrics/statpack.json`: September 14, 2026, 11:02 UTC. This is not a corpus last-pull measurement.
- No `fedcourts query` or `open-events` lookup was made; no ranged-corpus transfer line was emitted.

## CourtListener MCP

1. `search(type="o", citation="775 F.3d 816", num_results=3)`: one result, Motorola Mobility LLC v. AU Optronics Corporation, opinion 2755741, Seventh Circuit; metadata date November 26, 2014. The petition cites the reported decision as 2015. No conclusion depends on this metadata/year difference.
2. `search_document(opinion_id=2755741, query="determined by Motorola", snippet_size=1800)`: passage around reporter page 822 concerning price-setting by the domestic parent and separate foreign subsidiaries.
3. `search_document(opinion_id=2755741, query="trips up", snippet_size=1400)`: passage around reporter page 819 concerning the required causal connection between domestic effects and the claimed injury.

These were searches within an older precedent, not searches for the target petition or cases citing it. No target-case disposition was surfaced.

## Web attempts

- Search query: `site.supremecourt.gov Rule 10 considerations governing review certiorari conflict interlocutory`.
- Attempted open of the Supreme Court's `2023RulesoftheCourt.pdf` under its filing-and-rules page.
- Both web calls returned no usable content. No legal proposition or target-case information was drawn from them.

## Local contract operations

Read the governing prompt, instructions, schemas, path/ID/serialization helpers, event and provisioned record. Ran `fedcourts paths` for the specified cell. The initial invocation encountered a read-only default cache; using a writable temporary cache allowed it to run. These operations did not query the corpus or seek an outcome.
