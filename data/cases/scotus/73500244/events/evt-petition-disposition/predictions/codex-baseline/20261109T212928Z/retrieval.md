# Materials consulted

Baseline: the event definition, case-level context, November 9, 2026 snapshot, document manifest, questions presented, petition, BIO, reply, matching decision below, lower-court docket summary, and appendix excerpts including the rehearing order. Stable local references: `.github/prompts/predict.md`, prediction/flags/tooling schemas, and the cert sections of `metrics/statpack.md`. No other prediction or evaluation was read. No own-case outcome lookup was made.

# Corpus and CLI calls

1. `uv run fedcourts query --help` failed before executing the query interface: the default uv cache location was read-only. No transfer line. This was resolved by setting `UV_CACHE_DIR=/tmp/uv-cache`; `--no-sync` avoided dependency installation.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --help` succeeded and displayed structured-filter help. No transfer line.
3. `COLUMNS=150 UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --help` succeeded; its output was piped to `head -n 60` for a compact view. No transfer line.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --era modern --disposition granted --decided-before 2025 --limit 5` was rejected because `modern` is not an allowed decade token. It displayed the accepted vocabulary. No transfer line.
5. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts paths --court scotus --docket 73500244 --event evt-petition-disposition --role predictor` confirmed case/event paths and withheld the evaluator-only outcome path. No transfer line.
6. Corrected lookup: `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --era 2020s --disposition granted --decided-before 2025 --limit 5`. Returned five granted petitions; visible examples included RiseandShine, Monsanto, Hikma, and Cisco. No opinion bodies requested. The date filter is an October-Term filter, not a restriction to judgments before January 1, 2025; this is a forward cell. These selected grants were generic procedural comparators, not an empirical matched sample.

   Exact stderr transfer report: `ranged corpus reads: 80 GET(s), 20905984 byte(s)`.

# CourtListener MCP

1. `search(type="o", citation="140 F.4th 1257", num_results=3)` returned United States v. Chavarria, filed June 16, 2025, Tenth Circuit docket 23-2102, cluster 10605317, opinion 11071905. Used the preexisting lower-court opinion, not subsequent history.
2. `search_document(opinion_id=11071905, query="hold only", snippet_size=1800)` returned the concluding narrow holding and discussion of the generic motor-vehicle indictment. This supports discounting an unqualified split characterization.
3. `search_document(opinion_id=11071905, query="all cars", snippet_size=1000)` returned the discussion distinguishing automobiles from the broader motor-vehicle category and addressing Windham and Protho. Used with the first excerpt, not as a complete independent survey of the circuits.

# Web attempts

Three identical `web.run` open calls attempted the Tenth Circuit opinion PDF at `https://www.ca10.uscourts.gov/sites/ca10/files/opinions/010111250704.pdf`. Each returned no usable content or source text. One `web.run` search queried `site.ca10.uscourts.gov "23-2102" "Chavarria" "2025"`; it also returned no usable results. The chronological sequence was open, open, search, open. None informed the substantive forecast or surfaced this Supreme Court petition's disposition. The successful MCP excerpts supplied the needed primary-source check instead.

# Validation

Validation uses `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 PYTHONDONTWRITEBYTECODE=1 uv run fedcourts validate data --cell data/cases/scotus/73500244/events/evt-petition-disposition/predictions/codex-baseline/20261109T212928Z`. This is a local schema/completeness check, not case retrieval.
