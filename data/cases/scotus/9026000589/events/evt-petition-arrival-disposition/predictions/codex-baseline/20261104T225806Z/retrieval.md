# Retrieval log

## Local reference material and CLI setup

- Read `.github/prompts/predict.md`, the prediction and tooling schemas, the flags schema for reference, `metrics/statpack.md` (modern cert, originating-circuit, relist, CVSG, and prior-Term salience-band sections), and the claim-distribution declaration in `src/fedcourtsai/pipeline/claims.py`. These are instructions, schemas, aggregate priors, and label-contract checks, not other cells' outputs.
- Read the event definition and provisioned snapshot, context, document manifest, QPs, petition passages and opening appendix, separate decision below, lower-court docket summary, and same-question list. No outcome or other prediction was read.
- First attempted `uv run fedcourts paths --court scotus --docket 9026000589 --event evt-petition-arrival-disposition --role predictor` and `uv run fedcourts query --help`. Both failed before execution because uv's default cache path was read-only. Repeated both successfully with `UV_CACHE_DIR=/tmp/uv-cache`. The paths command identified the event and corpus; no evaluator-only file was opened. The help command described structured filters. These setup calls printed no ranged-read statistics.

## Corpus calls

1. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era modern --limit 4`
   - Rejected: `modern` is not an accepted decade token. No priors or transfer line returned. Corrected the filter rather than treating this as a corpus failure.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026 --limit 4`
   - Returned four granted petitions: U.S. DOGE Service, No. 25-1103; Corey Duran Berry, No. 25-7026; Todd Blanche v. Ozurumba, No. 25-1343; and Missionaries of Saint John the Baptist, No. 25-1131. The first and third federal petitions showed two distributions. Used only as weak procedural context, not as grant-rate observations. The Term filter concerns docket Terms; the returned grant dates in October 2026 preceded this November 4 run. No opinion bodies requested.
   - `ranged corpus reads: 38 GET(s), 9961472 byte(s)`
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --docket-number 26-210 --limit 1`
   - Returned the separate pending petition Trump v. Thakur, referenced in this petition, with one distribution for a scheduled November 13, 2026 conference, no disposition, and a November 2 last-poll date. No opinion body requested. Its QPs were not retrieved, so no exact companion relationship was assumed.
   - `ranged corpus reads: 10 GET(s), 2621440 byte(s)`

## Web attempts

1. One `web.run` call containing the searches `site.supremecourt.gov "Department of Education" "California" "24A910"` and `site.supremecourt.gov "National Institutes of Health" "American Public Health" "25A103"`. The tool returned no usable text or source references; neither search supplied evidence.
2. One `web.run` open attempt for the hypothesized official NIH PDF path `https://www.supremecourt.gov/opinions/24pdf/25a103_kh7p.pdf`. The tool returned no usable content or source reference. This guessed path was not verified and supplies no evidence.

Neither attempt searched this petition's outcome.

## CourtListener MCP calls

1. `search(type="o", citation="604 U.S. 650", court="scotus", num_results=2)` returned two representations of Department of Education v. California, dated April 4, 2025. Selected the original slip-opinion representation, opinion 10839607.
2. `read_document(opinion_id=10839607, chunk_index=0, chunk_size=9500)` returned the operative per curiam stay analysis and the beginning of Justice Kagan's dissent. Used to confirm the contractual-forum rationale and its preliminary posture. Did not read the remainder of the opinion.
3. `search(type="o", citation="606 U.S. 998", court="scotus", num_results=1)` returned zero results. No inference of nonexistent precedent drawn.
4. `search(type="o", court="scotus", case_name="National Institutes of Health v. American Public Health Association", filed_before="2026-11-05", num_results=1)` returned zero results. NIH's discussion remains attributed to the provisioned petition, not independent MCP verification.

No direct CourtListener REST calls, credential searches, package installations, or retrieval of this petition's disposition occurred.
