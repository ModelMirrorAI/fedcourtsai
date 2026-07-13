# Retrieval Log

- Provisioned inputs: Read the event definition, snapshot `2026-07-13.json`, `brief-in-opposition.txt`, and `questions-presented.txt`.
- Base rates: Consulted `metrics/statpack.md` for base rates on cert grants, relist counts, and originating courts.
- `web_fetch`: Retrieved the supplemental brief (dated June 25, 2026) directly from the Supreme Court docket at `https://www.supremecourt.gov/DocketPDF/25/25-246/414988/20260625114103616_Jouppi%20v.%20Alaska%20-%20Supplemental%20Brief.pdf` to determine why the case was held.
- `mcp_courtlistener_search`: Queried `"Pung v. Isabella County"` to verify the merits decision date (June 23, 2026) and its basic holding as referenced in the supplemental brief.