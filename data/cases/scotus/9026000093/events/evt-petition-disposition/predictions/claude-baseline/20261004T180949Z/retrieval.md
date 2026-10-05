# Retrieval log

Beyond the provisioned snapshot, context, petition text and questions-presented file:

## Corpus tooling
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8` → stderr: `ranged corpus reads: 12 GET(s), 3145728 byte(s)`. Returned recent grants (Marschner, DHS v. D.V.D., and several substantive applications); no structural match to a dueling-petition posture, not relied on.
- `metrics/statpack.md` (committed): modern cert disposition section, relist and CVSG cuts, salience band table (sal-v4). Pooled `elevated` bracketed `reached` rate over Terms 2017–2025 computed as 16.9% (n = 3085).

## CourtListener MCP
- `search(type=d, court=ca5, docket_number=24-10760)` → McNutt v. US Dept of Justice, filed 2024-08-20, terminated 2026-04-10.
- `search(type=d, court=scotus, q="McNutt OR Hobby Distillers OR distilling", filed_after=2026-01-01)` → 0 results (the SCOTUS dockets are not in the RECAP index).

## Web
- WebSearch: "McNutt v. Department of Justice Fifth Circuit home distilling en banc rehearing 2026" → learned the Fifth Circuit denied rehearing en banc on June 9, 2026 and that the government filed a cert petition on Aug. 14, 2026 (No. 26-204).
- WebFetch supremecourt.gov 26-93 Brief for the Federal Respondents (Aug. 14, 2026) — PDF saved and text extracted locally with pypdf. The government agrees review is warranted, asks the Court to grant McNutt and hold Ream, cites Ream's weaker standing and the unaddressed Commerce Clause question.
- WebFetch supremecourt.gov docket page 26-204 (twice: entries, then document links). DOJ v. McNutt docketed Aug. 18, 2026; BIO Sep. 17; waiver of 14-day period Sep. 18; distributed for the Oct. 9, 2026 conference and reply filed Sep. 23.
- WebFetch supremecourt.gov docket page 26-93 (document links; confirmed no entries after Sep. 23, 2026).
- WebFetch taxnotes.com article on the government's McNutt petition → HTTP 403, nothing read.
- WebFetch 26-93 Reply of petitioner (Sep. 1, 2026) — extracted locally. Asks the Court to grant Ream "whether or not it also grants McNutt"; argues the government has not disavowed the commerce theory.
- WebFetch 26-204 Brief for Respondents (Sep. 17, 2026) — extracted locally. Respondents agree certiorari is warranted and ask the Court to grant both and consolidate.
- WebFetch 26-204 Reply for the petitioners (Sep. 23, 2026) — extracted locally. Government: the only dispute is whether to grant or hold Ream; urges a hold, citing standing and the Court's single-petition practice (Anderson v. Intel, Murthy v. Missouri); disavows the commerce theory on any remand.

Total: 1 corpus query, 2 MCP searches, 1 web search, 9 web fetches (one failed). No retrieval sought or surfaced this petition's disposition; the Ream docket shows nothing past the Sep. 23 distribution and the conference is Oct. 9, 2026.
