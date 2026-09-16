# Retrieval record

- Read committed metrics/statpack.md: modern discretionary-cert dispositions, paid-segment relist and CVSG cuts, and the sal-v4 per-Term segment table. Read metrics/statpack.json to compute the state reached-rate pool over displayed Terms 2017–2024: 89 weighted grants / 392 weighted resolved petitions. No live corpus query or open-events call; no ranged-transfer line was emitted.
- Web search: `site.supremecourt.gov opinions 2020 Jones Mississippi 18-1259`. No usable result or source content returned.
- Web open: official Jones opinion PDF, `https://www.supremecourt.gov/opinions/20pdf/18-1259_8njq.pdf`. No usable source content returned.
- CourtListener MCP `search(type="o", citation="593 U.S. 98", num_results=1)`: Jones v. Mississippi, decided April 22, 2021; returned opinion ID 4679975, cluster 4876196. Used only to locate that precedent, not current citation counts.
- CourtListener MCP `search_document(opinion_id=4679975, query="as-applied", snippet_size=1600)`: majority discussion on slip page 21, plus a dissent passage. Used the majority's discretionary-procedure holding and express reservation of an as-applied disproportionality claim. No target-case outcome or subsequent history was sought or returned.
- Local operational reads: prompt, instructions, output schemas, and provisioned cell inputs. `uv run fedcourts paths --court scotus --docket 73281394 --event evt-petition-disposition --role predictor` initially failed because the default cache was read-only; rerunning with a writable temporary cache succeeded. This command resolves paths and does not retrieve corpus records.

No other case-specific external retrieval was performed. The reply brief listed in the snapshot was not fetched.
