# Retrieval record

## Provisioned evidence

Read the event definition, `record/context.json`, `record/snapshots/2026-10-08.json`, `record/documents/documents.json`, and the application and identified lower-court appendix passages in `record/documents/application.txt`. No other prediction, outcome artifact, or subsequent case history was read.

## Beyond the provisioned evidence

- Read `metrics/statpack.md`'s interim applications section and inspected the top-level keys of `metrics/statpack.json`. Ran `git log -1 --format='%h %cI' -- metrics/statpack.md` to identify the committed pack's version, not its underlying corpus freshness.
- A read-only stats-reviewer subagent inspected the interim statpack section and JSON metadata, verified the prior-Term pool of 53/549, and reported the parsing and selection limitations. It performed no case lookup, browsing, corpus access, or file writes.
- Web search: `site.supremecourt.gov Hollingsworth Perry 558 U.S. 183 190 stay reasonable probability fair prospect`. The tool returned no visible result payload.
- Web search: `Hollingsworth v Perry 558 U.S. 183 190 2010 stay`. The tool returned no visible result payload.
- Web open attempted the historical Cornell opinion address `https://www.law.cornell.edu/supct/html/09A648.ZPC.html`. The tool returned no visible content. These attempts supplied no evidence or case-outcome information.
- CourtListener MCP `search`: `type="o", citation="558 U.S. 183", num_results=1`, requesting case name, citations, filing date, opinions, and absolute URL. Returned *Hollingsworth v. Perry*, January 13, 2010, including lead opinion ID 9413203.
- CourtListener MCP `search_document`: `opinion_id=9413203, query="reasonable probability", snippet_size=650`. Read the passage at 558 U.S. 190 confirming the certiorari/reversal/irreparable-harm requirements and equitable balancing in close cases. This was a general historical precedent lookup, not retrieval about the forecast application.

No `fedcourts query` or `open-events` lookup was made; there are no ranged-corpus-read transfer lines. `fedcourts paths` was used only for path resolution. The initial invocation could not initialize the default read-only uv cache; retrying with a temporary cache succeeded. Contract/schema reads and final validation are local operational checks, not substantive case retrieval.
