# Retrieval record

## Local contract, record, and aggregate context

- Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, `schemas/agent_flags.schema.json`, and `schemas/agent_tooling.schema.json`; checked applicable instruction-file paths. Read the provisioned event, November 14 snapshot, context, document manifest, and complete application. No other prediction or evaluation was read.
- Attempted `uv run fedcourts paths --court scotus --docket 9526000686 --event evt-motion-disposition --role predictor`. It failed before lookup because the default uv cache was read-only.
- Retried as `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9526000686 --event evt-motion-disposition --role predictor`. It succeeded and identified the case, corpus, and event paths; no outcome was opened.
- Read `metrics/statpack.md`, specifically its interim and applicant-class sections, and the `interim` section of `metrics/statpack.json`. Local Python calculations pooled only Terms 2016–2025 for the applicable finer-reading base rate and applicant cuts: overall 156/1,337; private/capital 10/288. Earlier local inspection printed section keys, aggregate coverage fields, and available Term rows to identify the schema; no own-Term figure was used as an anchor.
- Ran `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` twice, the second time displaying its opening options to confirm filter spelling. Both help calls succeeded and read no case outcome.

## Corpus lookup

Command:

```text
UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition denied --era 2020s --decided-before 2026 --limit 3
```

Reported transfer:

```text
ranged corpus reads: 9 GET(s), 2293760 byte(s)
```

Returned Robert J. Jesenik v. United States (scotus/73500344), Andrew N. MacRitchie v. United States (scotus/73500351), and Tauno Waidla v. Christopher Pierce, Warden (scotus/73500384). These were unrelated cert denials, not matched stay applications. No opinion bodies were requested and these selected denials did not set the forecast. The year mask filters derived Term, not necessarily the calendar date on which a cert denial is entered. This forward cell's own case and linked petition were not queried.

## Web attempts

1. `web.run` search call with queries `site.supremecourt.gov "Woodard" "minimal procedural"` and `site.law.cornell.edu/supct/html/97-176.ZC.html Woodard`. The tool returned no usable result payload, snippets, or source text. No information was obtained or relied upon.
2. `web.run` open attempt for `https://www.law.cornell.edu/supct/html/97-176.ZC.html`. It likewise returned no usable payload. Nothing was obtained or relied upon; the attempted address was not treated as a verified citation.

## CourtListener MCP

1. `search(type="o", citation="523 U.S. 272", court="scotus", num_results=1)`: returned *Ohio Adult Parole Authority v. Woodard*, decided March 25, 1998, cluster 118189, including the opinion identifiers and excerpts. This lookup concerned historical clemency law only.
2. `read_document(opinion_id=9433600)`: returned Justice O'Connor's full concurrence in *Woodard*, 5,098 characters. Used for the distinction between minimal due-process safeguards and general judicial supervision of discretionary clemency. No search for this application's disposition or subsequent history was performed.

## Validation

Used the required cell-scoped `fedcourts validate data --cell` command with `UV_CACHE_DIR=/tmp/uv-cache`; validation results are reported by the command transcript. No package installation was attempted.
