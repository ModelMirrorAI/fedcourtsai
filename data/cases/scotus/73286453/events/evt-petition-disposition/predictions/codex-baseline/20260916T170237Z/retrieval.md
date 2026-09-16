# Retrieval beyond the provisioned inputs

- Read the committed `metrics/statpack.md`: modern discretionary-cert, originating-circuit, paid-segment relist/CVSG, and sal-v4 reached-band Term table. Used only 2017–2024 Term rows for the baseline anchor. Calculated the denominator-weighted average of the printed, rounded baseline reached rates locally: approximately 5.12025%, weighted n = 11,580.
- Web search batch: `site.supremecourt.gov "523 U. S. 833" "intentional misuse"` and `site.ca10.uscourts.gov "Browder" "2015" "1076"`. No usable results returned.
- Web search: `"County of Sacramento v. Lewis" "854"`. No usable results returned.
- CourtListener MCP `search(type="o", citation="523 U.S. 833", num_results=1)`: identified County of Sacramento v. Lewis, decided May 26, 1998, opinion 118214.
- CourtListener MCP `search_document(opinion_id=118214, query="intentional misuse", snippet_size=1500)`: read footnote 13 and adjacent footnotes; verified the language relied upon in the petition.
- CourtListener MCP `search(type="o", citation="787 F.3d 1076", num_results=1, fields=["caseName", "dateFiled", "opinions", "absolute_url"])`: identified Browder, decided June 2, 2015, combined opinion 2804970.
- CourtListener MCP `search_document(opinion_id=2804970, query="clearly established", snippet_size=1500)`: read the two overlapping excerpts covering reckless indifference, time for deliberation, and obviousness in the clearly-established-law analysis.

No corpus query or open-events lookup was made; no ranged-corpus transfer line was produced. No target-docket refresh, target disposition search, subsequent-history search, or opinion-citing search was performed. CourtListener results were used only for the two identified preexisting precedents, not for their citation counts or later metadata.

Operational reads included the prompt, schemas, and path resolver. The first `uv run fedcourts paths --court scotus --docket 73286453 --event evt-petition-disposition --role predictor` failed because the default cache directory was read-only; repeating it with a writable temporary cache succeeded. These were not substantive corpus retrievals.
