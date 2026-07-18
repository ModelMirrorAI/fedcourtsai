# Retrieval

- Committed base rates: `metrics/statpack.md` and `metrics/statpack.json`, including modern discretionary-cert disposition, originating-circuit, relist, CVSG, and Term/fee-class cuts.
- Corpus lookup: `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`
  - `ranged corpus reads: 149 GET(s), 39059456 byte(s)`
  - Returned five recent granted SCOTUS priors; all showed at least three conference distributions.
- CourtListener MCP opinion search: `("Help America Vote Act" OR HAVA) ("private right" OR "1983")`, limited to selected federal courts of appeals and opinions filed before July 18, 2026. It returned 13 results, including Eleventh Circuit HAVA cases.
- CourtListener MCP opinion search for the petition's principal split authorities: *Sandusky County Democratic Party v. Blackwell*, *Colon-Marrero v. Garcia-Velez*, *American Civil Rights Union v. Philadelphia City Commissioners*, *Crowley v. Nevada*, and *Bellitto v. Snipes*. Results confirmed that the cited cases involve differing HAVA provisions and postures.
- CourtListener MCP citation search for `606 U.S. 357`, followed by retrieval of opinion record 11084231: *Medina v. Planned Parenthood South Atlantic* (June 26, 2025). The syllabus and majority opinion supplied the governing § 1983/Spending Clause standard.

No search sought this petition's disposition or post-snapshot history.
