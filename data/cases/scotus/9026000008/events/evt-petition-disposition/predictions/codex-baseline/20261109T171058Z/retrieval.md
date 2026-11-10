# Retrieval beyond the provisioned case inputs

No search requested this petition's disposition, subsequent history, or coverage of its resolution. No other prediction, evaluation, outcome file, or `data/qp-topics/` material was read.

## Local reference material and CLI

- Read the prediction prompt, prediction schema, tooling and flags schemas, and committed `metrics/statpack.md` sections on modern dispositions, originating circuits, paid-segment relists, CVSG, amicus counts, and sal-v8 reached-band rates. These supplied the output contract and population context, not any individual case outcome.
- Attempted `uv run fedcourts paths --court scotus --docket 9026000008 --event evt-petition-disposition --role predictor`. It failed before execution because uv's default cache was on a read-only filesystem.
- Repeated as `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000008 --event evt-petition-disposition --role predictor`. It returned case, corpus, and event paths and explicitly withheld the evaluator-only outcome path. No corpus query was made, and no `ranged corpus reads` line was emitted.
- Read-only repository instruction/file listings and shell text/JSON inspection were used to locate and inspect the provisioned inputs. No additional case records were fetched through the CLI.
- Validation command for the completed cell: `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts validate data --cell data/cases/scotus/9026000008/events/evt-petition-disposition/predictions/codex-baseline/20261109T171058Z`. This is a local contract check, not retrieval of merits evidence.

## Web attempts

1. `web.run` search query `site.supremecourt.gov "Mirabelli" "Bonta" "2026"`. The tool returned no usable result text or source reference. No substantive fact was obtained from it.
2. `web.run` open of the attempted official-opinion address `https://www.supremecourt.gov/opinions/25pdf/25a810_b97d.pdf`. The tool returned no usable document text or source reference. I do not treat the guessed address as authenticated evidence. The discussion of Mirabelli instead relies on the provisioned petition, opposition, and reply.

## CourtListener MCP calls

1. `search(type="o", citation="895 S.E.2d 705", num_results=1)`, query id `22b90e72`. Returned a count of seven but displayed an unrelated Jones v. State result, not an exact verified citation match. That result was disregarded; remaining results were not opened.
2. `search(type="o", case_name="Vlaming v. West Point School Board", court="va", filed_before="2024-01-01", num_results=2)`, query id `b7e8e6ea`. Returned the Virginia Supreme Court's December 14, 2023 opinion, cluster 9451980, opinion 9909805. Used only as general preexisting legal context for assessing the asserted split.
3. `search_document(opinion_id=9909805, query="Garcetti", snippet_size=1300)`. Returned 69 matches, showing up to 20 snippets. The relevant majority discussion rejects a categorical official-duties defense and identifies the Virginia Constitution as the basis of its holding.
4. `search_document(opinion_id=9909805, query="even if our understanding", snippet_size=1100)`. Returned zero literal matches. This was not treated as disproving the BIO's quotation; HTML and text layout can interrupt literal strings.
5. `read_document(opinion_id=9909805, chunk_size=6000, chunk_index=[25,26,27])`. Returned opinion windows covering the majority's teacher-speech and Garcetti discussion, including the state-constitutional ground. The reading supports doctrinal tension but not the assertion of a square controlling federal conflict.

No CourtListener query concerned Polk's own Supreme Court docket or its disposition. No corpus priors were queried.
