# Retrieval record

The provisioned snapshot, context, application manifest, application text, and event definition were the only case-specific materials used. I made no own-case disposition, subsequent-history, live-docket, or decision-coverage request. No other prediction or evaluation was read.

## Local reference and tool setup

- Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, `schemas/agent_tooling.schema.json`, and `schemas/agent_flags.schema.json` for the contract; checked applicable instruction-file locations.
- `uv run fedcourts paths --court scotus --docket 9526000661 --event evt-motion-disposition --role predictor` failed before execution because the default uv cache was read-only. Reissued as `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts paths --court scotus --docket 9526000661 --event evt-motion-disposition --role predictor`; path resolution succeeded. No outcome file was opened.
- Consulted `metrics/statpack.md`'s interim section and applicant table, and used `jq` on `metrics/statpack.json`'s interim Term records to calculate 156/1,337 for Terms 2016–2025 and verify zero finer-unread counts.
- Ran `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --help`; repeated with `COLUMNS=160` and a `head -65` display to read options obscured by output truncation. Both succeeded and retrieved no case records.

## Corpus lookups

1. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --era 2020s --disposition denied --decided-before 2026 --limit 4`

   Transfer: `ranged corpus reads: 6 GET(s), 1572864 byte(s)`.

   Returned four unrelated cert denials: Robert J. Jesenik v. United States, Andrew N. MacRitchie v. United States, Tauno Waidla v. Christopher Pierce, Warden, and Eric Alan Isaacson v. Maribel Moses, et al. The filter uses a Term/year bar, not a requirement that every displayed disposition date precede calendar 2026. These are not matched interim priors and I did not use their outcomes to adjust the number or open their records.

2. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --citation '580 U.S. 206' --decided-before 2026 --limit 2`

   Transfer: `ranged corpus reads: 9 GET(s), 2359296 byte(s)`.

   No rows returned. The CLI warned that only 200 in-scope SCOTUS rows carry reporter citations and that the filter matches a case's own citations rather than cases citing it. I did not interpret the empty result substantively.

## Web attempts

- One `web.run` search request contained two searches: `site.supremecourt.gov opinions 2016 Peña-Rodriguez Colorado 15-606 pdf` and `site.supremecourt.gov Storey Lumpkin 2022 Sotomayor statement denial certiorari 21-7380`. The tool returned no usable results or text. No own-case search was made.
- One `web.run` open attempt targeted the official Peña-Rodriguez opinion at `https://www.supremecourt.gov/opinions/16pdf/15-606_886b.pdf`. The tool returned no usable content. I did not treat it as a successfully read source.

## CourtListener MCP

- `search(type="o", citation="580 U.S. 206", num_results=2)` verified **Peña-Rodriguez v. Colorado**, decided March 6, 2017, cluster 4374572, and exposed opinion IDs including 9873105. The response also included irrelevant reporter matches, which I disregarded. The returned text was partially truncated, but the matching case identification was visible.
- `search_document(opinion_id=9873105, query="unique", snippet_size=850)` returned one passage from the majority text distinguishing racial bias by its historical, constitutional, and institutional concerns. This supports the narrow-exception analysis, not any conclusion about Pavatt's own disposition. The case is **580 U.S. 206, 221–25 (2017)**; CourtListener path: `/opinion/4374572/pena-rodriguez-v-colorado/`.

The application itself supplied the discussion of Barefoot and Storey; I did not independently retrieve Storey's opinion or the Oklahoma decision. No full opinion bodies were hydrated from the corpus.
