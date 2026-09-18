# Retrieval beyond provisioned case inputs

- Read the committed `metrics/statpack.md`: modern discretionary-cert dispositions, paid-segment relist and CVSG cuts, and the matching `sal-v4` per-Term reached-band table. Only displayed Terms 2017–2024 were pooled for the numerical anchor. Inspected only the top-level key names of `metrics/statpack.json` for vintage metadata; no additional case records were read.
- No `fedcourts query` or `open-events` calls were made; there are no ranged-corpus transfer lines to report. The local `fedcourts paths` command was used to resolve the authorized event path, not to retrieve a prior or outcome.
- Web search: `site.loc.gov "Jones v. United States" "362" "257" hearsay warrant`. No usable results were returned.
- Web searches: `Jones v United States 362 US 257 269 hearsay` and `site.supremecourt.gov opinions Owen City Independence municipal qualified immunity`. No usable results were returned; no resulting pages were opened.
- CourtListener `search(type="o", citation="520 U.S. 397", num_results=1, fields=["caseName", "citation", "dateFiled", "opinions", "absolute_url"])`: located Board of the County Commissioners of Bryan County v. Brown, decided April 28, 1997; opinion 118104.
- CourtListener `search_document(opinion_id=118104, query="facially", snippet_size=1100)`: consulted the majority's distinction between directly unconstitutional action and facially lawful municipal action causing an employee's violation. The combined opinion also returned dissent snippets; those were not treated as holdings.
- CourtListener `search(type="o", citation="362 U.S. 257", num_results=1, fields=["caseName", "dateFiled", "absolute_url", "id"])`: returned an unrelated In re Chisum result and a field warning. Did not open that result or use it as evidence.
- CourtListener `search(type="o", case_name="Jones v. United States", citation="362 U.S. 257", filed_before="1961-01-01", num_results=1, fields=["caseName", "dateFiled", "absolute_url", "opinions"])`: located Jones, decided March 28, 1960; opinion 106022.
- CourtListener `search_document(opinion_id=106022, query="hearsay may be", snippet_size=650)`: verified the historical hearsay-warrant holding and its independent-magistrate rationale at 362 U.S. 270–271.

All external retrieval concerned historical precedent, not Mendenhall's disposition or subsequent history. Brief descriptions in the rationale are paraphrases of the provisioned filings, not external factual findings.
