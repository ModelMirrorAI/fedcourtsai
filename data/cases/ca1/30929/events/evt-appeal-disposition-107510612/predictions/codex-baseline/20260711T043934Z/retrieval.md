# Retrieval log

- Consulted `metrics/statpack.md`. Used the resolved First Circuit disposition base rate: `other` 86.3%, dismissed 8.0%, denied 5.0%, and granted 0.7% (599 resolved cases).
- Attempted a CourtListener MCP RECAP search limited to District of Puerto Rico docket `3:18-cv-01993` and filings before November 2, 2019, requesting only compact docket-entry fields. The service returned `REDIS_URL is not set; cannot access session store.` before executing the search; no results were consulted.
- Attempted `uv run fedcourts query --court ca1 --topic '3440 Other Civil Rights' --era 2010s --limit 10 --corpus-backend ranged`. It failed because the corpus remote hostname could not be resolved. No `ranged corpus reads: …` line was emitted and no prior was returned.
- Searched the local workspace for the caption and docket numbers to locate pre-decision material. Besides the provisioned event, the search output displayed only the path of a later same-party Supreme Court event. I did not open it or use it in the prediction; the inadvertent exposure is disclosed in `flags.json`.
