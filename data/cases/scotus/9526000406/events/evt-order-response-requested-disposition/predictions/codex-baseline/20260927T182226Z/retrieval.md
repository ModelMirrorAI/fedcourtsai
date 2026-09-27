# Retrieval beyond the provisioned inputs

## Committed base-rate context

- Read metrics/statpack.md, particularly “The interim docket (applications),” and the interim Terms in metrics/statpack.json. Consulted `git log -1 --format='%h %cI %s' -- metrics/statpack.md` to identify artifact revision 96ebdd342, September 26, 2026 at 12:03:37 UTC. Used only Terms 2016–2025 for the target's baseline.
- No `fedcourts query` or `fedcourts open-events` call was made; no ranged-corpus-read transfer line was produced. The path-resolution command is not a corpus lookup.

## General precedent, not target-case history

1. Web search: `site.supremecourt.gov opinions 2021 Garland Aleman Gonzalez 1252 f declaratory relief 596 543`. No usable result text was returned to this session.
2. Web search: `site.supremecourt.gov "Aleman Gonzalez" "declaratory" "2022"`. No usable result text was returned to this session.
3. Web open attempt: `https://www.supremecourt.gov/opinions/21pdf/20-322_m6hn.pdf`. No usable opinion text was returned through this tool.
4. CourtListener MCP `search(type="o", citation="596 U.S. 543", num_results=1, fields=["caseName", "citation", "dateFiled", "absolute_url", "opinions"])`. Returned Garland v. Gonzalez, June 13, 2022, including opinion ID 6349227 and the official Supreme Court download reference. Read the returned first result only.
5. CourtListener MCP `search_document(opinion_id=6349227, query="declaratory", snippet_size=800)`. Read the majority's footnote 2 reservation of the declaratory-relief issue and the separately identified dissent excerpts; did not confuse dissent with holding.
6. CourtListener MCP `search_document(opinion_id=6349227, query="take or to refrain", snippet_size=650)`. Read the majority's construction of the statutory injunction restriction.

No lookup sought application 26A406's disposition, post-snapshot docket entries, or coverage of its outcome. Earlier 2025 orders in the same litigation were encountered in the provisioned application itself, not retrieved as this event's answer.
