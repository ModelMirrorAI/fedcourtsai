# Retrieval record

## Local reference material

Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, `schemas/agent_flags.schema.json`, `schemas/agent_tooling.schema.json`, and the relevant cert sections of `metrics/statpack.md`, including the prior-Term salience risk sets and paid-segment relist, CVSG, and amicus cuts. Read the provisioned event and case record described in `reasoning.md`. No other cell's output was consulted.

## Corpus CLI calls

1. `uv run fedcourts query --help` failed before querying: the default cache `/home/codexcell/.cache/uv` was read-only. No corpus data returned and no transfer line printed.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` succeeded and displayed structured filter options. No corpus transfer line printed.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition gvr --era 2020s --decided-before 2026 --limit 3`
   - `ranged corpus reads: 37 GET(s), 9699328 byte(s)`
   - Returned Burford German Funding, No. 25-1269; Roofing Designs by JR, No. 25-1367; and Pedro Jose Silva Ochoa, No. 25-7569. All were marked GVR and lacked opinion bodies. Their October 2026 grant dates precede this forecast. The optional `--decided-before 2026` filter uses the corpus's Term/year mask, not a January 1 calendar-date ceiling. These are generic route examples, not substantive analogues, and did not drive the probability adjustment.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --docket-number 26-117 --limit 1`
   - `ranged corpus reads: 14 GET(s), 3670016 byte(s)`
   - Returned the pending Allen v. Milligan companion appeal, district case 2:21-cv-01530-AMM, three distributions and November 13, 2026 conference. No disposition recorded.
5. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --docket-number 26-118 --limit 1`
   - `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Returned the pending Allen v. Singleton companion appeal, district case 2:21-cv-1291-AMM, three distributions and November 13, 2026 conference. No disposition recorded. Zero transfer is the warm-cache report, not an omitted read.

The two companion lookups concern other proceedings expressly identified in the provisioned briefs. No query sought the current petition's own disposition. No `--full` hydration or `open-events` call was made.

## Web-tool attempts

All three attempts returned no usable tool response or source material. None informed the forecast:

1. Batched searches: `site.supremecourt.gov "Rule 11" "imperative public importance" certiorari before judgment` and `site.supremecourt.gov "Rule 10" "erroneous factual findings"`.
2. Open request for the official rules PDF at `https://www.supremecourt.gov/filingandrules/2026rulesofthecourt_web.pdf`.
3. Search: `Supreme Court Rule 11 certiorari before judgment imperative public importance`.

These requests sought general rules, not this case's outcome. No claim is made that the requested PDF was successfully retrieved or that its path was verified.

## CourtListener MCP

`search(type="o", citation="608 U.S. 511", court="scotus", num_results=3)` sought the earlier stay cited in the reply, not the disposition now being predicted. Query identifier `3cc0d587` returned one unrelated result, Staples v. United States, actually reported at 511 U.S. 600 (1994). I rejected that fuzzy mismatch and did not read or rely on its opinion. No further CourtListener call was made; no direct CourtListener REST request was used.

## Validation

The cell validator is run with `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts validate data --cell data/cases/scotus/9026000116/events/evt-petition-disposition/predictions/codex-baseline/20261109T171058Z`. It is a local output-contract check, not case retrieval.
