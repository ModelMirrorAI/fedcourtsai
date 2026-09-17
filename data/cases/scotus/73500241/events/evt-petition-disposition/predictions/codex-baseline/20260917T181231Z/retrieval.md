# Retrieval record

## Boundary

Forward mode; baseline snapshot September 17, 2026; no cutoff. No search sought this petition's Supreme Court disposition, subsequent history, or decision coverage. The appendix retrieval was confined to a filing already linked in the provisioned snapshot.

## Committed statistical context

- Read `metrics/statpack.md`: modern discretionary-cert dispositions, paid-segment relist and CVSG cuts, originating-court context, and the sal-v4 per-Term segment table.
- Read the corresponding structure and strictly prior baseline-reached fields of `metrics/statpack.json`; calculated the OT2017–OT2024 pooled anchor as 593 / 11,580.
- No `fedcourts query`, `open-events`, `stats`, or corpus pull was used. Consequently there are no ranged-corpus transfer lines to report. The committed pack's corpus-wide freshness was not independently established.

## External retrievals, in execution order

1. Browser `open` of the petition's filed appendix URL, copied from the snapshot: `https://www.supremecourt.gov/DocketPDF/25/25-1339/411933/20260528095752841_260521a%20Appendix%20for%20efiling.pdf`. No usable result returned.
2. CourtListener MCP `search(type="o", citation="111 F.4th 1249", num_results=2)`. One result: *Oyoma Asinor v. DC*, decided August 9, 2024, cluster 10035725, opinion 10502326. Used as a cited precedent, not as subsequent history of the target petition.
3. Browser `open` of the same appendix URL. No usable result returned.
4. Browser `find` on that URL for `qualified`. No usable result returned.
5. Browser `open` of the same appendix URL. No usable result returned. No web search query was issued.
6. CourtListener MCP `search_document(opinion_id=10502326, query="due process", snippet_size=550)`. Read seven returned excerpts, particularly slip opinion pp. 17–20 on overlapping constitutional protections.
7. CourtListener MCP `search(type="o", citation="576 P.3d 320", num_results=1)`. No result. This was a targeted lookup of the September 26, 2025 lower opinion, not the petition's Supreme Court outcome.
8. Shell-side `httpx.get` of the exact appendix URL above, with a 45-second timeout and redirects enabled; parsed in memory using `pypdf.PdfReader`. The PDF had 36 pages. Examined matching pages within the first 23 PDF pages for the terms `immunity`, `takings`, `fifth amendment`, `res judicata`, `limitations`, `due process`, or `abandon`. The returned lower-opinion passages establish the additional vehicle barriers. The transcript clipped some returned text; I rely on the visible passages, not unseen material. No PDF or extracted document was saved. This was a public Supreme Court filing request, not a CourtListener REST fallback.

## Local contract and operational reads

Read `AGENTS.md`, the prediction prompt, the prediction/tooling/flags schemas, and the path/serialization helpers. Used the path resolver with the authoritative court, docket, event, and predictor role. The first invocation failed because the default cache was read-only; the invocation with a temporary writable cache succeeded. Local schema checks and data validation are output checks rather than case retrievals.
