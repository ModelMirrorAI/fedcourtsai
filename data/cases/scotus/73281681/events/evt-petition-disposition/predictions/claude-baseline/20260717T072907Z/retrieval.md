# Retrieval log

Forward-mode cell. Beyond the provisioned inputs (snapshot, questions-presented,
petition text) and the committed `metrics/statpack.md` / `metrics/statpack.json`
base rates, I ran two corpus prior lookups; both returned zero rows (the corpus
citation index surfaced no resolved priors overlapping these citations).

1. `uv run fedcourts query --court scotus --citation "570 U.S. 595" --citation "483 U.S. 825" --citation "512 U.S. 374" --citation "601 U.S. 267" --limit 8`
   - stderr: `ranged corpus reads: 420 GET(s), 110100480 byte(s)`
   - 0 rows returned.
2. `uv run fedcourts query --court scotus --citation "570 U.S. 595" --limit 8`
   - stderr: `ranged corpus reads: 420 GET(s), 110100480 byte(s)`
   - 0 rows returned.

No CourtListener MCP lookups and no web searches were made; the provisioned
snapshot is dated today (2026-07-17) and carries the full docket, and the
petition text was provisioned in full. Base-rate context came from the
committed statpack (modern discretionary-cert disposition table, per-Term
paid/IFP grant rates in `statpack.json`, relist and CVSG cuts).
