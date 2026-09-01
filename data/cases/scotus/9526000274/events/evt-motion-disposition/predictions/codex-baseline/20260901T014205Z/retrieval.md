# Retrieval

## Corpus and base rates

- Read `metrics/statpack.md`, “The interim docket (applications),” including the per-Term substantive resolution and grant counts.
- Ran `uv run fedcourts query --court scotus --include-applications --limit 12` to inspect recent resolved priors. Transfer report: `ranged corpus reads: 4 GET(s), 1048576 byte(s)`.

## CourtListener MCP

- Searched Fourth Circuit RECAP for docket `26-1785`; located *Sherrod Brown v. FCC*, CourtListener docket 73519474.
- Retrieved the `docket-entries` endpoint schema.
- Retrieved the docket entries through August 31, 2026. This broad response was truncated but identified the petition, the August 25 divided opinion and judgment, the applicants' August 26 stay motion, and the August 27 denial of a stay.
- Attempted a ranged docket-entry lookup for entries 66–70; the API rejected the range syntax with HTTP 400.
- Retrieved docket entries 66, 67, 68, 69, and 70 individually, identifying RECAP document 491274464 (the published opinion), document 491551179 (the stay motion), and the lower court's stay denial.
- Read chunk 0 of RECAP document 491551179 and chunks 1–2 in a follow-up call, covering the full applicants' lower-court emergency stay motion.
- Read chunk 0 of RECAP document 491274464, covering the Fourth Circuit opinion's posture, panel division, and opening jurisdictional and merits analysis.
- Searched opinions for docket `26A124`; located *Trump v. California*, cluster 10956828.
- Searched opinions for citation `146 S. Ct. 2404`; no exact-citation result was returned.
- Searched Fourth Circuit RECAP for the United States/FCC response in docket `26-1785`; the search returned the merits response and the stay motion.
- Retrieved opinions for cluster 10956828 and identified opinion 11424433.
- Searched by exact case name for *National Republican Senatorial Committee v. FEC*; no result was returned.
- Read opinion 11424433, the August 24, 2026 per curiam in *Trump v. California*; the full response was truncated after exposing the majority's standing, ripeness, finality, and stay analysis and portions of the dissents.
- Searched opinions for `National Republican Senatorial Committee FEC coordinated expenditures`; located cluster 10882240 and the Fourth Circuit opinion in this litigation.
- Retrieved opinions for cluster 10882240 and identified opinion 11349765.
- Attempted to read opinion 11349765; CourtListener reported that no text was available.

## Other public filing

- Downloaded and extracted text from the Supreme Court PDF linked in the provisioned snapshot: the August 31, 2026 “Brief for the United States and the Federal Communications Commission as Respondents in Support of the Application.” The filing supports a stay and an immediate administrative stay; it contains no disposition of this application.
