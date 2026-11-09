# Retrieval record

## Provisioned inputs

Read the event definition, `record/context.json`, `record/snapshots/2026-11-09.json`, all three provisioned document texts and their manifest, both related snapshots and their manifest, and `record/same-question.json`. No other predictor's output, evaluator outcome, or QP-label artifact was read. Related dockets were read from the provisioned files, not queried externally.

## Local context and tooling

Read `.github/prompts/predict.md`, the prediction and feedback schemas, and the cert sections of `metrics/statpack.md`, including the prior-Term sal-v8 reached-band table and relist, CVSG and amicus cuts. The frozen context anchor is the principal baseline.

- `uv run fedcourts paths --court scotus --docket 9026000294 --event evt-petition-disposition --role predictor`: failed before execution because the default uv cache is read-only. No retrieval occurred.
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts paths --court scotus --docket 9026000294 --event evt-petition-disposition --role predictor`: succeeded, resolving the case and event paths; the evaluator-only outcome was not opened.
- `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --help`: consulted the structured interface. Repeated once with output limited to its final 75 lines to inspect the remaining flags. No corpus transfer line for help.

## Corpus lookups

1. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --citation '560 U.S. 305' --limit 2`
   - No matching rows. Explicit warning: only 200 in-scope rows carried reporter citations; empty results were not evidence that Samantar was absent from the law.
   - `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
2. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --disposition granted --era roberts --limit 3`
   - Rejected: era must be a decade token. The interface printed the permitted values. No transfer line was emitted.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026 --limit 3`
   - Returned Goldman Sachs Bank USA v. Brown (25-1408), U.S. DOGE Service v. United States District Court (25-1103), and Berry v. United States (25-7026), grant-filtered records with distribution counts four, two and five. No opinion text was requested or returned. These are not subject-matched FSIA priors and supply no estimated grant frequency. The Term mask was a conservative prior filter on this forward cell, not a replay cutoff.
   - `ranged corpus reads: 33 GET(s), 8650752 byte(s)`

## CourtListener MCP

- `search(type="o", citation="152 F.4th 339", num_results=2)`: searched for the decision below, not this petition's disposition. Returned count 0, query ID `4e900f71`. No lower-court opinion was retrieved.

## Web attempts

- One `web.run` call with two general-authority searches: `site.supremecourt.gov "Zivotofsky" "recognition" "2015" opinion` and `site.supremecourt.gov "Altmann" "merit no special deference"`. The tool returned no usable result content.
- One `web.run` open attempt for the House U.S. Code page for 28 U.S.C. § 1602, using the `granuleid:USC-prelim-title28-section1602` page. The tool returned no usable content. No external statutory text was incorporated.

No search sought this Supreme Court petition's disposition or later history. No outcome material surfaced.
