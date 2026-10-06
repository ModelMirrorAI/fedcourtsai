# Retrieval record

## Provisioned inputs

Read this cell's event definition, case-level context, October 5, 2026 snapshot, document manifest, questions presented, and substantive portions of the petition and brief in opposition. The related petition is discussed only as described in those inputs. No realized outcome or other predictor's artifact was read.

## Local aggregate context

- Read `metrics/statpack.md`: modern discretionary-cert dispositions, paid-segment relist and CVSG cuts, and the sal-v4 per-Term segment table.
- Read the structure and relevant segment values of `metrics/statpack.json`. Pooled elevated reached rates over rendered Terms 2017-2024 with `sum(prefix_est_grant_rate * prefix_weighted_resolved) / sum(prefix_weighted_resolved)`: 484 / 2810 = 0.17224199288256228. An initial structural inspection displayed the 2026 row; it was not used in the anchor.
- No `fedcourts query` or `open-events` call was made. There are no ranged-corpus transfer lines to report.

## External precedent only

1. Web search: `site.supremecourt.gov opinions Connick Thompson 09-571 563 51`. The tool returned no usable search content.
2. Web open: `https://www.supremecourt.gov/opinions/10pdf/09-571.pdf`. The tool returned no usable document content. Neither browser attempt supplied evidence.
3. CourtListener MCP `search`, `type="o"`, `citation="563 U.S. 51"`, `num_results=1`. Returned Connick v. Thompson, decided March 29, 2011, cluster 7343085, lead opinion 7261027; query identifier 034f869e. Used only as historical legal context.
4. CourtListener MCP `search_document`, `opinion_id=7261027`, `query="single-incident"`, `snippet_size=1000`. Read five excerpts concerning the narrow single-incident exception and insufficient additional-training theories, including the discussion at 563 U.S. 63-68. No later citing cases were sought.

No search requested this petition's disposition, subsequent history, or decision coverage. No outcome of this petition was encountered.

## Execution note

The first `uv run fedcourts paths --court scotus --docket 73500228 --event evt-petition-disposition --role predictor` attempt failed because the default uv cache directory was read-only. Retrying with a temporary writable uv cache succeeded. This was path resolution, not corpus retrieval. Output paths were also checked with `fedcourtsai.paths.CasePaths`.
