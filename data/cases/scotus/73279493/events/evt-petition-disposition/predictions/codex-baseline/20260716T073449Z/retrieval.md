# Retrieval

## Committed base-rate context

- Read `metrics/statpack.md` and `metrics/statpack.json`, including modern discretionary-cert dispositions, originating-circuit, relist, CVSG, Term 2025, and paid-fee-class rates.

## Corpus lookup

- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '523 U.S. 57' --era 2020s --limit 10 --corpus-backend ranged`
  - Failed before returning priors because the corpus remote hostname could not be resolved. No `ranged corpus reads: …` line was produced.

## CourtListener MCP

- Opinion search: `"willful and malicious injury" AND (subjective OR "substantial certainty") AND Geiger`, filed before July 16, 2026. The results confirmed substantial lower-court treatment of the competing intent formulations.
- Opinion search: `"objective substantial certainty" "subjective motive" "523(a)(6)"`, filed before July 16, 2026. Results included *MarketGraphics Research Group v. Berge*, 953 F.3d 907 (6th Cir. 2020), and other lower-court applications.
- Case-name search for *MarketGraphics Research Group v. David Berge* to identify the published Sixth Circuit opinion and its CourtListener opinion record.
- Retrieved the CourtListener opinion text for *Berge* (opinion ID 4520268). Consulted its discussion of the unitary/two-pronged circuit disagreement, subjective intent, and the proposition that intent may be inferred when the knowing act is itself the injury.
- Opinion search: `"false imprisonment" AND "523(a)(6)"`, filed before July 16, 2026. The results were dominated by the provisioned Eleventh Circuit decision in this case and fact-specific bankruptcy decisions, rather than a square contrary appellate false-imprisonment holding.

No web search was used, and I did not retrieve this case’s Supreme Court disposition or current docket.
