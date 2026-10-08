# Retrieval record

## Provisioned inputs

Read the event definition, case-level `context.json`, `snapshots/2026-10-08.json`, document manifest, questions presented, substantive petition sections and relevant appended Fifth Circuit opinion sections, and the opposition's certworthiness and statutory arguments. No outcome file, another predictor's output, or topic-labeling artifact was read.

## Additional local context

- Read the modern-cert, circuit, paid-segment relist/CVSG, and sal-v4 Term-band sections of `metrics/statpack.md`.
- Read matching prior-Term baseline risk-set fields in `metrics/statpack.json`; used `jq` to pool Terms 2017–2024, obtaining 593 / 11,580 = 0.05120898100172712.
- Ran `git log -1 --format='%h %cI' -- metrics/statpack.md` to identify the committed artifact vintage: `808f812e9`, September 28, 2026 at 12:02:50 UTC. This does not establish live corpus freshness.
- Ran `uv run fedcourts paths --court scotus --docket 73500293 --event evt-petition-disposition --role predictor`. The first attempt failed because the default cache was read-only; rerunning with a temporary writable cache succeeded. This was path resolution, not a corpus query.
- No `fedcourts query` or `open-events` call was made. There is no ranged-corpus transfer line to report.

## External lookups

1. Web search for `site.copyright.gov title17 304 c 6 E foreign laws termination`. The tool returned no usable content or source references. No case-specific outcome query was made.
2. Web open of `https://www.copyright.gov/title17/92chap3.html`. The tool again returned no usable content. The statutory discussion instead uses the provisions reproduced and argued in the provisioned filings.
3. CourtListener MCP `search`, type `o`, citation `155 F.3d 17`, maximum two results. Query identifier `4bf46d7a`. The results included an unrelated Gasser opinion and Fred Ahlert Music Corp. v. Warner/Chappell Music, Inc., Second Circuit, July 14, 1998, cluster 7070525, opinion 6974949. The unrelated result did not inform the forecast. The relevant snippet identifies the derivative-works exception as the issue.
4. CourtListener MCP `search_document`, opinion 6974949, literal query `foreign`, context 1,200 characters. Returned three overlapping passages explaining the retained foreign rights and separate domestic/foreign licenses. Used to assess whether this authority supplies a square circuit split. No full opinion was retrieved, and no broader negative claim about all precedent is inferred from this limited lookup.

No own-case disposition or subsequent-history material surfaced. The unsuccessful web requests were insufficient to independently verify the statute; the successful MCP lookup addressed only the scope of the cited 1998 precedent.
