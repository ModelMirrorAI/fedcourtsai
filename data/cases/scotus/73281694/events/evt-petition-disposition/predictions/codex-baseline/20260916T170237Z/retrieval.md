# Retrieval record

## Local context beyond the provisioned case inputs

- Read `metrics/statpack.md`: modern-cert dispositions, paid-segment relist and CVSG cuts, and the sal-v4 per-Term band table. Computed a denominator-weighted elevated/reached anchor using only displayed Terms 2017–2024: approximately 0.172379, denominator 2,810. No live corpus state was consulted.
- Ran `uv run fedcourts paths --court scotus --docket 73281694 --event evt-petition-disposition --role predictor`. The first attempt failed because the default cache was read-only; rerunning with a writable temporary cache succeeded. This command did not retrieve an outcome.
- No `fedcourts query`, `open-events`, or CourtListener MCP calls. No ranged-corpus-read transfer lines were emitted.

## Web tool attempts

These calls returned no usable results or source text:

1. Batched searches: `site.supremecourt.gov "Rule 10" "Compelling"` and `site.law.cornell.edu/uscode/text/28/1257 final judgments`.
2. Open: `https://www.supremecourt.gov/filingandrules/2023RulesoftheCourt.pdf`.
3. Open the July 14, 2026 reply PDF identified below, twice. Neither open returned content.

No search for this petition's disposition, current docket, subsequent history, or decision coverage was made.

## Successful official-PDF retrievals

Both URLs were copied from links in the provisioned snapshot, rather than discovered through a case-outcome search. PDFs were streamed into memory; no extra input files were written.

**Petitioner's reply brief, July 14, 2026**, especially pages 1–4 on amended pleadings, waiver, and finality, and pages 5–8 on importance and the constitutional argument:

`https://www.supremecourt.gov/DocketPDF/25/25-1208/416427/20260714114135771_Final%20-%20NS%20Mallory%20-%20Cert%20Reply.pdf`

- First shell attempt used `curl --fail --silent --show-error --max-time 45 <URL> | pdftotext - -`; it failed because `pdftotext` was unavailable and produced no extracted text.
- Retried with `curl` piped to `uv run python`, using `pypdf.PdfReader` over an in-memory byte stream. Read the extracted reply, then fetched it again to display PDF pages 5–8 separately because the initial tool display was truncated.

**Appendix to the April 17, 2026 petition**, especially pages 1a–3a containing the relevant state-court orders and the reproduced Hunt material beginning at 4a:

`https://www.supremecourt.gov/DocketPDF/25/25-1208/403563/20260417113844287_Norfolk%20Appendix%20-%20Final.pdf`

- Retrieved through the same `curl`/in-memory `pypdf` pipeline.
- Repeated the retrieval to display PDF pages 6–8, including appendix pages 4a–6a, separately after the first display was truncated.

The appendix contains lower-state-court dispositions and related Hunt proceedings, not the Supreme Court disposition of this petition. The provisioned BIO references a May 4, 2026 denial in the separate Lynn/BNSF case; that is pre-snapshot related-case context. No outcome of this cell's event was encountered.
