# Retrieval record

## Provisioned inputs and local context

- Read the case-level October 17, 2026 snapshot, context, event definition, document manifest, extracted questions presented, petition argument, and selected appendix orders. No outcome artifact or other predictor's output was read.
- Read the modern discretionary-cert, paid-segment relist/CVSG, and per-Term sal-v4 segment sections of `metrics/statpack.md`. Used `metrics/statpack.json` only for the exact baseline reached rates and weighted denominators over Terms 2017–2025. A local `jq` calculation produced 643 grant-equivalents / 12877 weighted resolved petitions = 0.04993399083637493. No current-Term rate entered the prior.
- Read the prediction, tooling, and flags schemas and the task instructions. These are output-contract references, not case-outcome retrieval.
- Ran `uv run fedcourts paths --court scotus --docket 9026000512 --event evt-petition-arrival-disposition --role predictor`; the initial attempt failed on a read-only cache and the retry with a temporary writable cache succeeded. This resolves paths, not case outcomes.
- No `fedcourts query` or `open-events` calls; therefore no ranged-corpus transfer line was generated. No corpus blob was pulled and no independent claim of corpus freshness is made.

## Web requests

Only general rules, statutes, and historical precedent were requested; no search contained this petition's caption or docket number. The web tool returned no readable source text in this session, so these attempts supplied no independently usable factual evidence or case outcome. Their requests are recorded for completeness:

1. Search batch: `site.supremecourt.gov Rule 10 considerations governing review certiorari`; `site.uscode.house.gov 28 1257 final judgments decrees highest court State`; `site.loc.gov Abney United States 431 651 1977`.
2. Open `https://www.supremecourt.gov/filingandrules/rules_guidance.aspx`.
3. Search batch: `site.loc.gov "Dowling v. United States" "493" "342"`; `site.uscode.house.gov "2241" "in custody"`.
4. Open `https://www.govinfo.gov/content/pkg/USCODE-2023-title28/pdf/USCODE-2023-title28-partIV-chap81-sec1257.pdf`.
5. Retry the Supreme Court rules-guidance page.
6. Open `https://www.govinfo.gov/content/pkg/USCODE-2024-title28/pdf/USCODE-2024-title28-partVI-chap153-sec2241.pdf`.
7. Search `Supreme Court Rule 10 considerations governing review on certiorari`.
8. Retry the Supreme Court rules-guidance page.
9. Search batch: `28 USC 2241 custody`; `28 USC 1257 final judgments`.
10. Literal find for `erroneous factual findings` in `https://www.supremecourt.gov/filingandrules/2026RulesoftheCourt_WEB.pdf`.

Rule 10 and the statutory framing in the rationale are general legal context, not claimed extracts from these unsuccessful requests. The prediction does not rely on a purported recent amendment or development. The supplied petition itself invokes Section 1257, Section 2241, Abney, and Ashe; the retrieved Abney text independently supports the appellate-procedure distinction and the qualification concerning state double-jeopardy finality.

## CourtListener MCP

1. `search(type="o", citation="431 U.S. 651", num_results=3)`: returned unrelated 2013 cert-denial records because the citation search matched other reporter components. These were not used as analogous cases or as grant-rate evidence; no own-case material appeared.
2. `search(type="o", case_name="Abney v. United States", court="scotus", filed_before="1978-01-01", num_results=2, fields=["caseName", "dateFiled", "citation", "opinions", "absolute_url"])`: located the June 9, 1977 decision, opinion 109677, 431 U.S. 651, and a 1976 cert-grant entry. Used the 1977 opinion, not the grant entry as a prior.
3. `search_document(opinion_id=109677, query="1291", snippet_size=900)`: checked the federal appellate jurisdiction question and the opinion's discussion of Section 1257.
4. `read_document(opinion_id=109677, chunk_index=2, chunk_size=8000)`: read the collateral-order analysis and the discussion of Harris v. Washington concerning finality for a state's rejection of a pretrial double-jeopardy claim. This prevents treating presentence status alone as a categorical jurisdictional bar.

No direct CourtListener REST request was made. No target-case disposition or subsequent history was encountered.
