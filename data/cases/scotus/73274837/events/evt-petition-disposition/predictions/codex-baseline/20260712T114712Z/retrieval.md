# Retrieval beyond provisioned inputs

- Consulted `metrics/statpack.md`, especially “Modern discretionary-cert petitions by disposition.” It reports 10 grants, 189 denials, and 5 dismissals among 204 resolved denial-reweighted modern petitions, a 4.9% grant rate.
- Attempted corpus priors with `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --topic "Second Amendment" --limit 8`. The request failed before returning any rows because the corpus object-store hostname could not be resolved (`EndpointConnectionError`). No `ranged corpus reads: …` line was produced, so no priors from this command informed the forecast.
- CourtListener MCP opinion search: `q="\"large capacity magazines\" Second Amendment arms"`, opinions filed before 2026-07-12, 10 results. The results confirmed the relevant appellate landscape, including *National Association for Gun Rights v. Lamont* (Second Circuit, 2025), *Duncan v. Bonta* (Ninth Circuit, 2025), and *Hanson v. District of Columbia*.
- CourtListener MCP opinion search: `q="Bensen \"large capacity magazine\" Second Amendment"`, opinions filed before 2026-07-12, 10 results requested. It returned only unrelated *State v. Max Misch* results and did not inform the forecast.
- CourtListener MCP opinion search: `q="Bensen firearm magazine Second Amendment"`, opinions filed before 2026-07-12, 10 results requested. It returned only unrelated *State v. Max Misch* results and did not inform the forecast.
- CourtListener MCP opinion search: `q="Benson Brown magazine ban Second Amendment"`, opinions filed before 2026-07-12, 10 results. The results were mostly unrelated; no result materially informed the forecast.
- CourtListener MCP opinion search: `case_name="Bensen"`, opinions filed before 2026-07-12, 20 results. The results were unrelated and did not inform the forecast.

No web searches or REST fallback calls were used.
