# Retrieval record

## Local contract, provisioned record, and aggregate context

Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, `schemas/agent_tooling.schema.json`, and `schemas/agent_flags.schema.json`; the specified event definition; the case-level snapshot dated 2026-11-11; context; document manifest; and the provisioned application. No other prediction/evaluation trees or realized outcomes were read.

Read the interim and applicant-class sections of `metrics/statpack.md` and the corresponding `interim.terms` records in `metrics/statpack.json`. Computed the 2016–2025 finer-reading pool and private/unmarked cut locally. No aggregate command fetched case outcomes.

## CLI attempts

1. `uv run fedcourts paths --court scotus --docket 9526000684 --event evt-motion-disposition --role predictor` failed because the default uv cache location was read-only. No corpus request occurred.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9526000684 --event evt-motion-disposition --role predictor` succeeded and confirmed the event path. Its outcome placeholder was evaluator-only and was not opened.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` succeeded. Read the structured filter interface before querying.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition denied --era modern --limit 3` was refused: `modern` is not a valid decade token. No transfer line was printed. The usage response supplied the accepted vocabulary.
5. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition denied --era 2020s --decided-before 2026 --limit 3` succeeded. Transfer: `ranged corpus reads: 9 GET(s), 2293760 byte(s)`. Returned Robert J. Jesenik v. United States (25-7515), Andrew N. MacRitchie v. United States (25-7522), and Tauno Waidla v. Christopher Pierce, Warden (25-7555), all unrelated cert denials dated November 9, 2026. The Term filter admits prior-Term dockets; these resolution dates precede this application's submission as well. No application-specific information or other forecast surfaced. These rows were not used to estimate interim relief probabilities.
6. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --citation '556 U.S. 418' --decided-before 2026 --limit 1` succeeded with no rows. Transfer: `ranged corpus reads: 9 GET(s), 2359296 byte(s)`. The tool warned that only 195 scoped rows carry reporter citations and an empty citation lookup reflects coverage limits. No full opinions were hydrated.

The forward-mode context has no replay clock. The explicit prior-Term filters were voluntary precautions against retrieving the present application's disposition. No installs, live docket lookups, or CourtListener MCP calls were made. The required cell validator was run locally after writing the outputs.

## General-law web calls

Only precedent and legal standards were sought; no query named this application, its applicant, its docket, or an outside forecast.

1. One `web.run` search call with queries `site.supremecourt.gov Hollingsworth Perry 558 183 190 stay reasonable probability fair prospect` and `site.law.cornell.edu supremecourt Liteky 510 540 judicial rulings alone almost never bias`.
2. One `web.run` open call for the Justia reproduction of *Hollingsworth v. Perry*, 558 U.S. 183 (2010).
3. One `web.run` search call with query `site.supremecourt.gov opinions 08pdf Nken Holder 08-681 434 2009`.
4. One `web.run` open call for Cornell LII's *Nken v. Holder* opinion, docket 08-681.

These web calls supplied no visible result text in this execution. Consequently no retrieved web passage was used as evidence. The governing stay formulation was available in the provisioned application, printed pages 20–21; legal citations in the rationale identify that standard and the familiar general recusal rule rather than claiming successful independent web verification. The unsuccessful external access does not prevent a record-based prediction.
