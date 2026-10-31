# Retrieval record

## Local contract, tooling, and base-rate context

- Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, and `schemas/agent_tooling.schema.json`; inspected repository instruction-file locations and working-tree status without reading other predictions, evaluations, or outcome files.
- Attempted `uv run fedcourts paths --court scotus --docket 9026000369 --event evt-petition-disposition --role predictor` and `uv run fedcourts query --help`. Both failed because `/home/codexcell/.cache/uv` was read-only. No retrieval occurred on these attempts.
- Retried both commands with `UV_CACHE_DIR=/tmp/uv-cache`. Paths resolved the expected case and event, explicitly withholding the evaluator-only outcome. Query help described the structured filters. Read the help's options again before issuing queries. No package installation was performed.
- Read `metrics/statpack.md`: modern-cert disposition and circuit tables, paid-segment relist/CVSG/amicus cuts, and the sal-v4 prior-Term reached-band table. Used the exact frozen `cert_anchor` in provisioned context as the principal anchor.

## Corpus lookups

1. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '544 U.S. 280' --limit 2`
   - `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - No matching row. Coverage warning: only 200 SCOTUS rows in scope carry reporter citations; absence is not evidence that *Exxon Mobil* does not exist.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --disposition denied --decided-before 2026 --limit 3`
   - `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Returned *Google LLC v. VirtaMove*, 25-1230 (two distributions), *Hastings College Conservation Committee v. California*, 25-1231 (two), and *Ryan O'Donnell v. City of Chicago*, 25-1098 (four), each denied October 19, 2026. The year filter is a docket-Term filter, not a calendar-year date cutoff. These are different cases, already decided before the October 31, 2026 snapshot. No opinion bodies were requested. No topical analogy or empirical rate was inferred from this disposition-selected sample.

## Web attempts

1. `web.run` search query: `site.supremecourt.gov "Skinner" "independent claim" "Rooker"`. Returned no usable content.
2. `web.run` search batch: `site.supremecourt.gov/opinions "T. M." "2026" Rooker` and `site.supremecourt.gov/opinions "Skinner" "562" "521"`. Returned no usable content. No search sought Loop's disposition or later history.

## CourtListener MCP

1. `search(type="o", court="scotus", case_name="T. M. v. University", num_results=3)` returned two versions of the June 18, 2026 Supreme Court opinion in docket 25-197, including the June 19 revised version. These are precedent, not the target petition.
2. `read_document(opinion_id=11345156, chunk_index=0, chunk_size=10000)` returned the opening syllabus of the revised *T. M.* opinion. It confirms that Rooker-Feldman can apply while state appellate review remains available and describes the barred request to invalidate and enjoin a consent order. The primary opinion source identified by CourtListener is `https://www.supremecourt.gov/opinions/25pdf/25-197_new_4g15.pdf`. Only the opening 10,000-character chunk was read, not the complete 150,948-character combined document.

The target case's facts and procedural state came from the provisioned record. No live lookup of its own disposition, subsequent history, other predictor outputs, evaluator outcomes, or topic-label artifacts was made.
