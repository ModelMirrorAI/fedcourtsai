# Retrieval

- Consulted `metrics/statpack.md`, especially “Modern discretionary-cert petitions by disposition,” “Modern cert petitions by originating circuit,” and the 2025 Term row. It reports a 4.9% estimated modern-cert grant rate and a 6.7% grant rate for the Eleventh Circuit cut.
- Attempted `fedcourts query --court scotus --citation '599 U.S. 1' --citation '478 U.S. 30' --decided-before 2025 --limit 5 --corpus-backend ranged` to retrieve pre-2025 priors while excluding this case. The command failed before reading the corpus because the remote host could not be resolved; it printed no `ranged corpus reads` line and returned no priors.
- CourtListener MCP search: opinions search for `"certiorari before judgment" "Voting Rights Act"`, restricted to the Supreme Court and filings before August 26, 2025, to confirm pre-petition legal context without seeking this case's disposition. The five returned records included *Allen v. Milligan*, 599 U.S. 1 (2023), and *Department of Commerce v. New York*, 588 U.S. 752 (2019). Only the *Allen* identification informed the analysis.
- No web search or REST fallback was used. No retrieval sought this case's outcome.
