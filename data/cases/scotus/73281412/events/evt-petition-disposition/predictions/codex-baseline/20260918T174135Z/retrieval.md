# Retrieval record

## Committed aggregate context

- Read `metrics/statpack.md`: modern discretionary-cert dispositions, originating-circuit cut, paid-segment relist and CVSG cuts, and sal-v4 per-Term segment table. Also inspected headings to locate the relevant sections.
- Read `metrics/statpack.json` structure and current-version segment fields. Computed the elevated reached-rate pool only for displayed Terms 2017–2024: weighted grants 484, weighted resolved denominator 2,810, pooled rate 0.17224199288256228. Did not use current or later Terms as the numeric anchor, alternative salience versions, or merits/interim rates.
- No `fedcourts query` or `open-events` call was made; no ranged-corpus transfer line was produced.

## External attempts and precedent

1. Web search, batched queries: `site.supremecourt.gov opinions Taylor Riojas 2020 19-1261 per curiam` and `site.supremecourt.gov Rule 10 certiorari misapplication properly stated rule law`. The tool returned no usable results or source text.
2. Web open of the Taylor opinion PDF at `https://www.supremecourt.gov/opinions/20pdf/19-1261_bq7c.pdf`. The tool returned no usable text.
3. CourtListener MCP `search`: type `o`, citation `592 U.S. 7`, two results requested, fields caseName/dateFiled/citation/opinions/absolute_url. Identified Taylor v. Riojas, November 2, 2020, opinion ID 4582848, cluster 4802501. An unrelated historical bank-case hit was also returned and not used.
4. CourtListener MCP `read_document`, opinion ID 4582848. Read Taylor's general confinement/qualified-immunity reasoning and summary correction, with its procedural differences from Alexander. No search for this cell's own case or outcome was performed.

## Local operations

Read the agent instructions, prediction contract, relevant output schemas, and provisioned case files. Ran `fedcourts paths --court scotus --docket 73281412 --event evt-petition-disposition --role predictor`; the initial invocation failed on a read-only default cache and the retry using a temporary writable cache succeeded. Local schema validation does not supply forecasting evidence.
