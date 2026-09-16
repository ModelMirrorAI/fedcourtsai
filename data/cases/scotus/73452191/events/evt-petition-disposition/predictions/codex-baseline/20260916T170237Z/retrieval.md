# Retrieval log

## Local context beyond the provisioned record

- Read the committed `metrics/statpack.md`: modern discretionary-cert disposition and circuit sections; paid-segment relist and CVSG sections; Term and sal-v4 band table. Used only 2017–2024 rows for the band anchor. A local read-only arithmetic command pooled the displayed baseline reached rates to approximately 5.12025%, weighted denominator 11,580.
- Read the task contract and artifact schemas. Ran `fedcourts paths` for the supplied cell identifiers. The first `uv run` attempt failed because its default cache directory was read-only; pointing the cache at a writable temporary directory allowed the command to run.
- No `fedcourts query` or `open-events` calls, no full corpus pull, and no ranged-corpus transfer lines.

## Web attempts

1. Search queries: `site.loc.gov "Mireles v. Waco" "502"` and `site.ca4.uscourts.gov "Gibson" "Goldston" "2023"`. Tool returned no usable content.
2. Attempted to open the official Fourth Circuit opinion path `https://www.ca4.uscourts.gov/opinions/221757.P.pdf`. Tool returned no usable content; no opinion or proposition was verified through this attempt.

## CourtListener MCP

1. `search(type="o", citation="502 U.S. 9", num_results=1)`: returned an irrelevant Glaxo patent case; disregarded, not read further.
2. `search(type="o", case_name="Mireles v. Waco", court="scotus", num_results=1, fields=["caseName", "dateFiled", "citation", "opinions", "absolute_url"])`: identified *Mireles v. Waco*, 502 U.S. 9 (October 21, 1991), opinion 112655.
3. `read_document(opinion_id=112655)`: retrieved Mireles; displayed output was truncated.
4. `search_document(opinion_id=112655, query="police", snippet_size=700)`: examined the judicial-function analysis and allegations.
5. `read_document(opinion_id=112655, chunk_index=3, chunk_size=3000)`: read the targeted majority discussion at reporter pages 12–13. Used as a general preexisting legal comparator, not as information about this petition's outcome.

No retrieval sought or surfaced this petition's disposition or subsequent history. No outcome files or labeling-measurement artifacts were consulted.
