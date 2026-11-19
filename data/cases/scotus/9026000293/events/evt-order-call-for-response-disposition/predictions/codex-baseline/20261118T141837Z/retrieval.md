Beyond the provisioned case record, I consulted the committed prediction/output schemas and the relevant portions of `metrics/statpack.md`, plus the top-level structure of `metrics/statpack.json`. The prior-Term high-band anchor and the frozen amicus comparison were checked against the provisioned context. No web search was attempted, no current docket for this petition was retrieved, and no other prediction or evaluation was read.

CLI setup and attempted calls:

- `uv run fedcourts paths --court scotus --docket 9026000293 --event evt-order-call-for-response-disposition --role predictor` failed before retrieval because uv's default cache path was read-only. No transfer line was printed.
- `uv run fedcourts query --help` failed for the same reason, before retrieval. No transfer line was printed.
- `UV_NO_CACHE=1 uv run --no-sync fedcourts paths --court scotus --docket 9026000293 --event evt-order-call-for-response-disposition --role predictor` succeeded and reported the case ID, corpus path, and event path. It did not disclose an outcome path.
- `UV_NO_CACHE=1 uv run --no-sync fedcourts query --help` succeeded. I read the structured-filter and timing-mask documentation.

Corpus lookups:

1. `UV_NO_CACHE=1 uv run --no-sync fedcourts query --court scotus --era 2020s --disposition gvr --decided-before "${DECIDED_BEFORE:-2026}" --limit 3`
   - Returned Christina Casarez v. Irigoyen Farms, No. 25-1421; Roybal v. Griffith, No. 25-442; and Harrington v. Martin, No. 25-1348. Their GVR dates were November 16, November 9, and November 9, 2026, respectively, all before this cell's cutoff. The Term filter screens docket-number Terms rather than guaranteeing a decision before calendar 2026. Roybal also showed a prior CVSG. None had an opinion body. Used only as procedural examples, without inferring a base rate from a grant-selected sample.
   - `ranged corpus reads: 28 GET(s), 7340032 byte(s)`
2. `UV_NO_CACHE=1 uv run --no-sync fedcourts query --court scotus --citation "146 S. Ct. 1909" --decided-before "${DECIDED_BEFORE:-2026}" --limit 1 --full`
   - No rows returned. The CLI warned that only 195 SCOTUS rows in scope carry any reporter citation, so the empty result is a coverage limitation rather than evidence that CIMEX does not exist.
   - `ranged corpus reads: 8 GET(s), 2097152 byte(s)`

CourtListener MCP lookups, all concerning the separately decided CIMEX precedent rather than this petition's outcome:

1. `search` with `type="o"`, `court="scotus"`, `q='caseName:("Exxon Mobil" AND "CIMEX")'`, `filed_before="2026-11-18"`, `num_results=3`, and fields `caseName,dateFiled,citation,cluster_id,absolute_url,docketNumber,opinions`.
   - One result: Exxon Mobil Corp. v. Corporacion CIMEX, S.A. (Cuba), No. 24-699, decided June 23, 2026; cluster 10878536, combined opinion 11346053. The citation field was empty.
   - https://www.courtlistener.com/opinion/10878536/exxon-mobil-corp-v-corporacion-cimex-s-a-cuba/
2. `read_document` with `opinion_id=11346053`, `chunk_index=[0,1,2]`, `chunk_size=8000`.
   - Read the first 24,000 characters of the 92,681-character combined opinion, including the complete syllabus and the opening majority discussion. It confirms the Helms-Burton immunity-abrogation holding and its four statutory considerations.
3. `search_document` with `opinion_id=11346053`, `query="recognition"`, `snippet_size=400`.
   - Zero matches in the complete combined opinion.
4. `search_document` with `opinion_id=11346053`, `query="Terrorism Risk"`, `snippet_size=500`.
   - Zero matches in the complete combined opinion.
5. `search_document` with `opinion_id=11346053`, `query="primary responsibility"`, `snippet_size=500`.
   - One match, in the majority's discussion of the FSIA's history and the Helms-Burton Act's presidential suspension authority. The snippet confirmed the context of the proposition quoted by petitioners.

Tool metadata was inspected to discover the MCP search and document-reading signatures. No CourtListener REST fallback was used. Local file-reading commands consulted only the instructions, schemas, statpack, provisioned record, and this cell's own outputs; validation is a local completeness/schema check, not an additional legal-source retrieval.
