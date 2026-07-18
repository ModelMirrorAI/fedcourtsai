# Retrieval Log

- Attempted CourtListener MCP search: `q="\"Padilla\" AND \"collateral consequence\" AND \"Sixth Amendment\" AND (\"civil\" OR \"estoppel\" OR \"False Claims Act\")"` 
  - Result: HTTP 429 Rate limit exceeded.
- Waited for rate limit to clear.
- Attempted CourtListener MCP search: `q="\"Padilla\" AND \"collateral consequence\" AND (\"Sixth Amendment\" OR \"ineffective assistance\") AND \"estoppel\""`
  - Result: Retrieved 10 clusters including *Farhane v. United States* (2d Cir. 2023, 2024), *Nita Patel v. United States* (3d Cir. 2025 - the lower court opinion), and state cases like *State v. Denisyuk* (Md. 2010).
- Read corpus base rates via the static file `metrics/statpack.md`.
  - Found that the base rate for paid cert petitions is generally around 2.5% - 3.5%, and that circuit rates are broadly low. The statpack also details the impact of relists and CVSGs.