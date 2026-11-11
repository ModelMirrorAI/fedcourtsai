# Retrieval record

## Provisioned material

Read the event definition; case-level snapshot `2026-11-10.json`; `context.json`; document manifest; questions presented; substantive petition and portions of its appendix; the substantive responses in the combined opposition file; cert reply; opening, holding, and targeted portions of the matching lower-court opinion; lower-court docket summary; related manifest; and the three provisioned companion snapshots, Nos. 26-199, 26-332, and 26-335. These are provisioned inputs, not fresh retrievals. Did not read another prediction, evaluation, or realized outcome.

## Committed base-rate context

Read `metrics/statpack.md`: modern discretionary-cert dispositions, originating-circuit cuts, paid-segment relist/CVSG/amicus cuts, salience-band context, and the sal-v8 per-Term reached table. Only rows strictly before OT2026 inform the band anchor. Used the frozen `cert_anchor` in the provisioned context as the authoritative numerical baseline.

## Corpus and CLI attempts, in order

1. `uv run fedcourts paths --court scotus --docket 9026000201 --event evt-petition-disposition --role predictor` — failed before execution because uv could not initialize its default cache on the read-only filesystem. No corpus response or transfer line.
2. `uv run fedcourts query --help` — same cache failure. No query executed or transfer line.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts paths --court scotus --docket 9026000201 --event evt-petition-disposition --role predictor` — succeeded, confirming the case and event paths. No transfer line. Did not access an outcome.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --help` — succeeded, displaying structured-filter usage. No corpus query or transfer line.
5. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --disposition granted --era modern --limit 3` — rejected: `modern` is not a valid decade token; the tool supplied the valid vocabulary. No results or transfer line.
6. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026 --limit 3` — succeeded. Exact transfer report: `ranged corpus reads: 37 GET(s), 9699328 byte(s)`. Returned Goldman Sachs Bank USA v. Brown, No. 25-1408 (grant November 6, 2026; four distributions); U.S. DOGE Service v. U.S. District Court for the District of Columbia, No. 25-1103 (grant October 13, 2026; two distributions); and Corey Duran Berry v. United States, No. 25-7026 (grant October 13, 2026; five distributions). No opinion text was requested or returned. These were broad mechanical examples of granted petitions, not subject-matched comparators; no substantive case-specific inference or empirical grant frequency is drawn from this grant-filtered sample. The bare `2026` clock filters by earlier docket Term, not by grant date. None is the target case.

## Web attempts

Two `web.run` search calls sought general precedent on private delegation, not the target petition's disposition:

1. Query: `site.supremecourt.gov opinions 2024 FCC Consumers Research 24-354 private delegation June 27 2025`.
2. Query: `site.supremecourt.gov "24-354" "2025" "Research"`.

Both returned no visible results, excerpts, or source identifiers. No webpage was opened and no external factual proposition was adopted. The reference to *Consumers' Research* in the forecast comes from the provisioned filings and lower-court opinion.

## Other operations

Read the prediction contract and output schemas, checked for applicable AGENTS.md files, inspected local file lists and git status without reading git history or other outputs, and checked the UTC time and patch-tool availability. These did not retrieve legal material. The final cell-validation command checks only this output cell and is not a corpus lookup. No CourtListener MCP lookup, direct REST call, package installation, or own-case disposition search was attempted.
