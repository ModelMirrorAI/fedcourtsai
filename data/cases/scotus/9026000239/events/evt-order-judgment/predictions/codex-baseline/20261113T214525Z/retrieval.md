# Scope

Used the provisioned snapshot dated November 13, 2026, context, event definition, document manifest, and all six provisioned text documents. No later record of this case, other predictor output, evaluator outcome, or third-party forecast was retrieved. The following are all attempted lookups beyond those inputs, including unsuccessful calls.

# Local reference material and CLI setup

- Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, `schemas/agent_tooling.schema.json`, and `schemas/agent_flags.schema.json` for the output contract.
- Consulted the merits, per-Justice-votes, and authorship portions of `metrics/statpack.md` / `metrics/statpack.json`, and the merits-baseline cautions in `metrics/README.md`. Computed prior-Term pools locally from the committed JSON; no corpus transfer was involved. Did not use the cert salience-band rates.
- Attempted `uv run fedcourts paths --court scotus --docket 9026000239 --event evt-order-judgment --role predictor`. It failed before execution because the default uv cache was read-only.
- Repeated as `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000239 --event evt-order-judgment --role predictor`. It succeeded and returned the case, corpus, and event paths, with the outcome described only as evaluator-only. No outcome file was read.
- Ran `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` three times, the later two with wider `COLUMNS` settings and output selection to read the structured-filter interface. Help itself made no corpus lookup.

# Corpus queries

1. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era roberts --decided-before 2026 --limit 5`
   - Rejected: `roberts` is not a valid era; the command printed the accepted decade vocabulary. No transfer line was emitted.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026 --limit 5`
   - Succeeded. Exact stderr: `ranged corpus reads: 42 GET(s), 10944512 byte(s)`.
   - Returned five cert-granted rows: Goldman Sachs v. Brown (25-1408), U.S. DOGE Service v. District Court (25-1103), Berry v. United States (25-7026), Blanche v. Ozurumba (25-1343), and Missionaries of Saint John the Baptist v. Frederic (25-1131). Their merits judgments were null. The bare-year filter does not make these recent cert-grant rows a historical merits sample. They supplied no substantive analogue and did not move the prediction.

# Web attempts

1. One `web.run` search call with these three precedent/statute-only queries:
   - `site.supremecourt.gov opinions "Aleman Gonzalez" "1252(f)(1)"`
   - `site.uscode.house.gov "1158" "irrespective" "consistent with this section"`
   - `site.supremecourt.gov "Trump v. Hawaii" "contravene" "statutory"`
   - The tool returned `Search failed`; no search snippets or case-outcome material were available.
2. `web.run` direct open of `https://www.supremecourt.gov/opinions/21pdf/20-322_m6hn.pdf`.
   - Returned `Found no tool response`. No document content was obtained.
3. `web.run` direct open of `https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title8-section1158&num=0&edition=prelim`.
   - Returned `Found no tool response`. No statutory content was obtained from this call.

# CourtListener MCP

1. `search(type="o", citation="596 U.S. 543", num_results=2)`.
   - Returned *Garland v. Gonzalez* / *Garland v. Aleman Gonzalez*, June 13, 2022, docket 20-322, cluster 6477116, opinion 6349227; also an unrelated second result that was not used. Search query ID: `9c1b7254`.
2. `search_document(opinion_id=6349227, query="We hold", snippet_size=1500)`.
   - Returned two excerpts identifying the holding that §1252(f)(1) barred the classwide detention injunctions, together with the statutory text and procedural posture.
3. `search_document(opinion_id=6349227, query="collateral", snippet_size=1100)`.
   - Returned three excerpts. The majority's footnote 4 distinguishes injunctions against uncovered provisions with collateral effects on covered provisions. The dissent excerpts did not supply the holding.
4. `search_document(opinion_id=6349227, query="joined", snippet_size=850)`.
   - Returned the syllabus lineup: Alito wrote for Roberts, Thomas, Gorsuch, Kavanaugh, and Barrett; Sotomayor wrote separately, with Kagan and Breyer joining to the stated extents. Used as precedent-specific coalition and authorship context, not a forecast of this case.

# Validation

The final cell is checked with `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts validate data --cell data/cases/scotus/9026000239/events/evt-order-judgment/predictions/codex-baseline/20261113T214525Z`. Validation is a local contract check, not substantive retrieval.
