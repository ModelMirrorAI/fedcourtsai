# Retrieval log

## Committed context

- Read the interim-docket section of `metrics/statpack.md` and the top-level keys of `metrics/statpack.json`. Computed the eligible prior-Term pool from the Markdown table: 31/301. Inspected the pack's last modifying commit with `git log -1 --format='%h %cI' -- metrics/statpack.md`: `3f3ca14f4 2026-10-08T21:56:24Z`.
- Ran `uv run fedcourts corpus-info` to seek corpus vintage. It failed because the service backend has no client-side connection. No corpus rows or freshness values were returned and no ranged-read transfer line was printed. No `fedcourts query` or `open-events` lookup was made.
- Ran `uv run fedcourts paths --court scotus --docket 9526000416 --event evt-brief-response-disposition --role predictor` for the prescribed path check. This is not case-outcome retrieval.

## Respondents' pre-decision filing

The snapshot identifies the response as filed October 8, 2026. Used only that filing's exact URL, not a docket search or subsequent-history lookup:

```text
https://www.supremecourt.gov/DocketPDF/26/26A416/428868/20261008145929279_2026.10.08%20Respondents%20Opposition%20to%20Stay%20Application%20-%20Trump%20v.%20Kingdom%2026A416.pdf
```

- A `web.run` open of this URL returned no usable content.
- Retrieved the same URL with Python `urllib.request.urlopen`, receiving HTTP 200, `application/pdf`, 365837 bytes. The first extraction attempt failed because `pymupdf` was unavailable.
- Four subsequent reads of this same immutable filing used the installed `pypdf.PdfReader` in memory. The PDF has 52 pages. Inspected PDF pages 2, 7–9 (contents/authorities), 12–16 (printed pp. 1–5), 42–46 (printed pp. 31–35), and 47–51 (printed pp. 36–40). Thus there were five shell HTTP GETs in total, all to this one pre-decision filing. No downloaded document was written to disk.
- The opposition's arguments informed the downward adjustment and partial-relief risk. No decision, post-cutoff case development, or outcome-revealing material was encountered.

No CourtListener MCP lookup or web search was performed. Local instructions, schemas and provisioned inputs were also read for the output contract.
