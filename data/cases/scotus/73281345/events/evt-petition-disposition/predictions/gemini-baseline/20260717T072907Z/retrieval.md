# Retrieval Log

- Consulted `metrics/statpack.md` to establish modern discretionary-cert base rates (general grant rate ~3.2%; Fifth Circuit origin grant rate ~4.8%).
- Executed MCP CourtListener search (`court: ["ca5"], q: "United States v. Elkins"`) to verify the Fifth Circuit decision and found cluster 10750700 (161 F.4th 899).
- Executed MCP CourtListener search (`court: ["ca10"], q: "United States v. Chavarria"`) to verify the Tenth Circuit decision and found cluster 10605317 (140 F.4th 1257).
- Attempted `fedcourts query --court scotus --limit 5 --corpus-backend ranged` to pull priors, but the remote corpus environment was unavailable.
- Used the provisioned docket snapshot, event details, and `questions-presented.txt` as primary input facts.
