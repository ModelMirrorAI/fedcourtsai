# Retrieval record

## Provisioned and stable inputs

Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, the event definition, the case-level November 14 snapshot, context, document manifest, questions presented, petition with appendix, matched decision below, lower-court docket extract, and same-question list. Read the relevant modern-cert, paid-segment relist/CVSG/amicus, and sal-v8 per-Term tables in committed `metrics/statpack.md`. Consulted tooling and flags schemas to determine output shapes. No other predictor's output, evaluation, or outcome artifact was read.

## CLI setup and corpus lookups

1. `uv run fedcourts paths --court scotus --docket 9026000631 --event evt-petition-arrival-disposition --role predictor` failed before execution because `/home/codexcell/.cache/uv/CACHEDIR.TAG` was on a read-only filesystem. No retrieval occurred and no transfer line was printed.
2. Reissued as `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000631 --event evt-petition-arrival-disposition --role predictor`. It returned the case id, corpus path, and expected event path. A later identical invocation returned the same paths. No outcome was opened; the paths command labels it evaluator-only. No transfer lines.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` returned the structured query interface. A later `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help | head -70` reread its opening options. Neither retrieves corpus rows or prints transfer statistics.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition denied --era modern --limit 3` was rejected: `modern` is not an era token; the interface requires a decade such as `2020s`. No corpus results or transfer line.
5. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition denied --era 2020s --decided-before 2026 --limit 3` succeeded. Stderr: **`ranged corpus reads: 8 GET(s), 2031616 byte(s)`**. It returned Robert J. Jesenik v. United States (25-7515), Andrew N. MacRitchie v. United States (25-7522), and Tauno Waidla v. Christopher Pierce, Warden (25-7555), each recorded denied November 9, 2026. The Term filter admitted these prior-Term dockets; the actual decision dates precede this forward cell's snapshot. These generic denial-filtered rows were not substantive analogues and supplied no frequency estimate. No full opinion bodies requested.

## Other attempted retrieval

6. `web.run` search queries: `site.supremecourt.gov Rule 10 considerations governing review certiorari` and `site.uscode.house.gov 38 5109A claimant request review 5121 accrued benefits`. The tool returned no visible result or usable content. No factual or legal claim was taken from this attempt.
7. `web.run` open of the official Court rules PDF at `https://www.supremecourt.gov/ctrules/2023RulesoftheCourt.pdf`. Again no visible result or usable content. No rule text was retrieved or relied upon.
8. CourtListener MCP `search(type="o", citation="63 F.4th 27", num_results=1)` returned query id `34064786`, count 0, results empty. This was a lookup of Crews, an authority in the provisioned opinion, not this petition's outcome. No inference about the precedent's existence or validity follows from the empty result.

No search targeted this petition's disposition or another person's forecast. No outcome-revealing or forecast material about this petition surfaced. Validation and local schema inspection are output checks, not additional factual retrieval.
