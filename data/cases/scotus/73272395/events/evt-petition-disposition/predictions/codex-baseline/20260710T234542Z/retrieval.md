# Retrieval

- Consulted `metrics/statpack.md` for committed Supreme Court petition base-rate context. The file did not contain the prompt-described modern discretionary-cert section; its 2025 Term row had no resolved cases.
- Attempted `fedcourts query --court scotus --citation "Strickland v. Washington" --era 2020s --limit 10 --corpus-backend ranged`. The storage endpoint could not be resolved before any corpus rows were returned, so the command printed no `ranged corpus reads: ...` line.
- Attempted a CourtListener opinions search for `"cumulative error" "ineffective assistance" Strickland`, limited to filings before July 11, 2026. It returned no results because the configured session store was unavailable.
- Attempted a CourtListener opinions search for `"genuinely deadlocked" "poll" jury "manifest necessity"`, limited to filings before July 11, 2026. It returned no results because the configured session store was unavailable.
- No web searches were used.
