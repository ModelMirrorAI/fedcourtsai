# Retrieval log

- `uv run fedcourts query --court scotus --citation "590 U.S. 432" --limit 3` printed `ranged corpus reads: 10 GET(s), 2621440 byte(s)`. No rows came back, and a coverage note said the citation column is sparse.
- `uv run fedcourts query --court scotus --disposition granted --limit 5` printed `ranged corpus reads: 24 GET(s), 6291456 byte(s)`. It returned five recent granted dockets, none of them topically related, so they did not inform the forecast.
- `uv run fedcourts query --help` was run for usage only.
- WebFetch of the supremecourt.gov docket page for 25-1383, done twice (once for the entries, once for the PDF links). It showed the BIO (8/26/2026), the reply (9/9/2026) and a distribution for the 11/6/2026 conference. The petition is still pending.
- WebFetch of the BIO PDF and the cert reply PDF. The fetch tool could not read either. I extracted text from the saved PDFs locally with pypdf and read the BIO's table of contents and summary of argument, and the reply's headings.
- Static read of `metrics/statpack.md` for base rates.
- No CourtListener MCP calls.
