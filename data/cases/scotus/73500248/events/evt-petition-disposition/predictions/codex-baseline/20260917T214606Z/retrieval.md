# Retrieval record

## Local context

- Read the task contract and prediction/tooling schemas, the assigned event, and provisioned case inputs identified in `reasoning.md`.
- Consulted `metrics/statpack.md`: modern discretionary-cert dispositions, originating-circuit context, paid-segment relist/CVSG cuts, and the sal-v4 per-Term reached-rate table. Used `metrics/statpack.json` only for the corresponding 2017–2024 baseline risk-set counts and exact rates. The weighted pool is 593 / 11,580 = 0.05120898100172712.
- Ran `uv run fedcourts paths --court scotus --docket 73500248 --event evt-petition-disposition --role predictor`. The default cache was read-only; retry with a writable temporary cache succeeded. This resolves paths, not case content.
- No `fedcourts query` or `open-events` lookups were performed; no ranged-corpus transfer lines were produced. No remote corpus freshness claim is made.

## Web attempts

The web tool returned no usable result content for these searches, and they supplied no substantive evidence:

1. `site.supremecourt.gov opinions Murphy Smith 2018 1997e 150 percent`
2. `site.supremecourt.gov Rule 10 certiorari judicial discretion`
3. `Murphy v Smith 583 U.S. 220 2018 150 percent`

None targeted this petition's outcome or subsequent history.

## CourtListener MCP

1. `search(type="o", citation="583 U.S. 220", num_results=2)`: returned Murphy v. Smith, filed February 21, 2018, cluster 4469601, opinion 4246854. An unrelated George v. Roberts result was disregarded; no pagination followed.
2. `search_document(opinion_id=4246854, query="150", snippet_size=600)`: read eight matching excerpts, distinguishing the majority's first-sentence allocation issue from the dissent's description of the second-sentence cap. Used only as pre-existing legal context, not as a directly controlling holding on Webb's question.

No current case docket, Supreme Court disposition, subsequent history, another predictor's output, or outcome artifact was retrieved.
