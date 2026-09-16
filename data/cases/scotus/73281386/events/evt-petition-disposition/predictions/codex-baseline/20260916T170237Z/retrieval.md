# Retrieval beyond the provisioned record

- Read the committed `metrics/statpack.md`: modern discretionary-cert disposition counts, paid-segment relist and CVSG cuts, and the sal-v4 per-Term band table. Read only the top-level key names of `metrics/statpack.json`; no additional numerical estimates were taken from that JSON. The matched anchor uses the markdown's 2017–2024 baseline reached rows.
- No `fedcourts query` or `open-events` calls; no ranged corpus reads or transfer lines.
- Ran `fedcourts paths --court scotus --docket 73281386 --event evt-petition-disposition --role predictor` for path resolution, not case retrieval. The first attempt failed because the default uv cache was read-only; the retry with a writable temporary cache succeeded.
- Web search: `site.supremecourt.gov opinions 2003 Cheney 542 U.S. 367 discovery separation powers`. No usable source text was returned to this session.
- Web open: `https://www.supremecourt.gov/opinions/boundvolumes/542bv.pdf`. No usable source text was returned to this session. No search sought DOGE's petition disposition or subsequent history.
- CourtListener MCP `search(type="o", citation="542 U.S. 367", num_results=1)`: returned Singleton v. Astrue, 542 F. Supp. 2d 367 (2008), an unrelated reporter match; disregarded.
- CourtListener MCP `search(type="o", court="scotus", case_name="Cheney", filed_after="2004-01-01", filed_before="2004-12-31", num_results=3, fields=["caseName","dateFiled","opinions","absolute_url","citation"])`: verified the June 24, 2004 Cheney decision and supplied metadata/snippets, including lead opinion ID 9434668. Other returned results were 2004 procedural orders; they supplied no forecast signal.
- CourtListener MCP `search_document(opinion_id=9434668, query="vacat", snippet_size=1400)`: HTTP 429, rate limited; no opinion passage returned. Proceeded with provisioned materials rather than direct REST retrieval.

The June 6, 2025 Supreme Court order used in reasoning was read from the provisioned petition's Appendix A, not newly retrieved. It concerns an earlier petition/application, not the disposition being forecast.
