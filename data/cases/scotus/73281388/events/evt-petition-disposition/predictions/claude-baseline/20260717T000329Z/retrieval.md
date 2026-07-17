# Retrieval log — scotus/73281388 · evt-petition-disposition · claude-baseline · 20260717T000329Z

Beyond the provisioned inputs (snapshot, questions-presented, petition, brief
in opposition) and the committed `metrics/statpack.md` / `metrics/statpack.json`,
the following corpus lookups were made. All returned zero rows; the prediction
therefore rests on the provisioned inputs and the statpack base rates.

1. `uv run fedcourts query --court scotus --citation "565 U.S. 400" --citation "482 U.S. 691" --era 2020s --limit 6`
   - stderr: `ranged corpus reads: 419 GET(s), 109707264 byte(s)`
   - 0 priors returned.
2. `uv run fedcourts query --court scotus --citation "565 U.S. 400" --era 2020s --limit 8`
   - stderr: `ranged corpus reads: 419 GET(s), 109707264 byte(s)`
   - 0 priors returned.
3. `uv run fedcourts query --court scotus --topic "Fourth Amendment" --era 2020s --limit 8`
   - stderr: `ranged corpus reads: 3 GET(s), 786432 byte(s)`
   - 0 priors returned.

No CourtListener MCP lookups were made (forward-mode cell; the provisioned
snapshot and full-text petition/BIO already carried the decision-relevant
docket signals, and searching risked no upside worth the calls). No web
searches were made.
