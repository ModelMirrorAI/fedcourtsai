# Retrieval record

## Local materials beyond the provisioned case inputs

- Read AGENTS.md, .github/prompts/predict.md, and the prediction, agent-tooling, and agent-flags schemas for the output contract.
- Ran `uv run fedcourts paths --court scotus --docket 73287447 --event evt-petition-disposition --role predictor`. The initial attempt failed because the default uv cache was read-only; rerunning with `UV_CACHE_DIR=/tmp/uv-cache` succeeded. No outcome file was opened.
- Read `metrics/statpack.md`: modern discretionary-cert dispositions, originating-circuit rates, paid-segment relist and CVSG cuts, and the sal-v4 Term/band table. Read the JSON companion's coverage and Term segments and used jq to pool elevated prefix rates over the displayed 2017–2024 Terms: 484 / 2810 = 0.17224199288256228.
- Ran `git log -1 --format='%h %cI' -- metrics/statpack.md` to identify the pack-file vintage: September 14, 2026 at 11:02 UTC. This is not a corpus pull timestamp.
- No `fedcourts query`, `open-events`, corpus pull, or live corpus lookup was used; consequently there are no ranged-corpus transfer lines.

## Web attempts

1. One search call with the queries `City Oakland Oakland Raiders 20 F.4th 441 459 footnote 11 bright line nonpurchasers` and `Montreal Trading Amax 661 F.2d 864 regular course dealing 868`. The tool returned no usable results or text.
2. Attempted to open the Ninth Circuit's December 2, 2021 opinion PDF at `https://cdn.ca9.uscourts.gov/datastore/opinions/2021/12/02/20-16075.pdf`. The tool returned no usable content. No substantive inference depends on these web attempts.

## CourtListener MCP

1. `search(type="o", citation="20 F.4th 441", num_results=2)` returned City of Oakland v. Oakland Raiders, filed December 2, 2021; cluster 5302474, opinion 5131036.
2. `search_document(opinion_id=5131036, query="bright-line", snippet_size=1200)` returned the majority's footnote rejecting a categorical nonpurchaser bar and a separate opinion discussing that issue. The rationale relies on the majority's footnote, not the separate opinion.
3. `search_document(opinion_id=5131036, query="regular course", snippet_size=1300)` returned the majority's discussion of speculative causation and Oakland's alleged course of dealing in an anticompetitive market.
4. `search_document(opinion_id=395374, query="regular course", snippet_size=1300)` returned Montreal Trading's passage explaining how prior dealings can reduce speculation; the opinion identifier appeared in the preceding citation-linked result.

All retrieved substantive opinions predate this petition. No search sought this petition's disposition, subsequent history, or prior predictions, and no outcome-revealing material was encountered.
