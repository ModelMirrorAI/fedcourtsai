# Retrieval

## Corpus base rates

- Consulted `metrics/statpack.md`, especially “Modern discretionary-cert petitions by disposition,” “Modern cert petitions by originating circuit,” “Cert petitions by relist count,” “Cert petitions by CVSG status,” and the 2025 Term row.
- Consulted `metrics/statpack.json` for the 2025 Term fee-class estimate: paid petitions had an estimated 5.36% grant rate.

## Corpus prior lookup

- Command: `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '441 U.S. 520' --era 2020s --limit 8 --corpus-backend ranged`
- Result: failed before returning priors because the corpus remote hostname could not be resolved. No `ranged corpus reads: …` line was printed.

## CourtListener MCP

- Opinion search, filed before July 17, 2026: `("suicide prevention" OR "suicide watch") "excessive in relation" "pretrial detainee"`. The 24 results included the pre-petition Fifth Circuit opinions and decisions such as *Pittman v. Madison County*, *Short v. Hartman*, and *Miranda v. County of Lake*. This was used only to assess whether the questions sit in a developed body of circuit law.
- Opinion search, filed before July 17, 2026: `("suicide watch" OR "suicide prevention") "Bell v. Wolfish" excessive`. The 91 results included appellate and district-court applications across several circuits. The search supported treating the underlying doctrine as recurring, but it did not establish a clean conflict on this petition's exact rule and facts.
- Citation search for `165 F.4th 309`, filed before July 17, 2026: no results.
- Full-text opinion search for `"165 F.4th 309"`, filed from December 23, 2025 through July 16, 2026: no results.

No web search was used. No search sought or revealed this petition's disposition.
