# Retrieval record

## Provisioned and committed materials

Read the prediction prompt and prediction/tooling/flag schemas; the specified event; the case-level November 16, 2026 snapshot, context, document manifest, questions presented, petition with retained appendix, and lower-court docket extract; `related/related.json` and staged dockets 26-292 and 26-294; and `same-question.json`. Read relevant committed `metrics/statpack.md` sections: modern discretionary-cert dispositions, originating circuits, paid-segment relist/CVSG/amicus cuts, salience bands, and prior-Term sal-v8 reached rates. No other cell's prediction or evaluation was opened, and no QP-topic artifact was read.

## Corpus CLI and operational discovery

1. `uv run fedcourts paths --court scotus --docket 9026000293 --event evt-order-cvsg-disposition --role predictor` initially failed because uv's default cache was read-only. It retrieved no case data.
2. `UV_CACHE_DIR=/tmp/fedcourts-uv-cache uv run fedcourts query --help` succeeded. The help was consulted a second time with `| tail -78` to inspect remaining flags. These are interface reads, not priors.
3. `UV_CACHE_DIR=/tmp/fedcourts-uv-cache uv run fedcourts paths --court scotus --docket 9026000293 --event evt-order-cvsg-disposition --role predictor` succeeded and resolved the event/corpus paths. The command labels the realized outcome evaluator-only; no outcome file was read.
4. `UV_CACHE_DIR=/tmp/fedcourts-uv-cache uv run fedcourts query --court scotus --disposition gvr --era modern --limit 4` was rejected: `modern` is not a valid decade token. No corpus transfer line was returned. Reissued with the documented `2020s` token rather than abandoning retrieval.
5. `UV_CACHE_DIR=/tmp/fedcourts-uv-cache uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 4` returned Casarez (25-1421), Huffman (26-5528), Roybal (25-442), and Harrington (25-1348). Roybal had a June 30 CVSG and three distributions before its November 9, 2026 GVR. No returned prior had an opinion body. These are procedural examples, not substantively matched sovereign-immunity cases; they do not estimate a grant rate.

   `ranged corpus reads: 28 GET(s), 7274496 byte(s)`

6. `UV_CACHE_DIR=/tmp/fedcourts-uv-cache uv run fedcourts query --court scotus --docket-number 24-699 --full --limit 1 | jq '{case_name,disposition,date_decided,has_opinion,opinion_text:(.opinion_text // "" | .[0:12000])}'` looked up the cited CIMEX precedent after the MCP document failure. The row identified Exxon Mobil v. Corporación Cimex but had `date_decided: null`, `has_opinion: false`, and no body. Its petition-level `granted` label does not independently establish the merits holding. `--full` supplied no additional text; no opinion-body transfer was observed.

   `ranged corpus reads: 18 GET(s), 4718592 byte(s)`

7. Repeated the corrected four-prior query, projecting `case_id`, caption, docket number, disposition, grant date, CVSG date, distribution count, and opinion availability with `jq -c` to make the initially lengthy output readable. Results were unchanged. Casarez and Huffman were recorded GVRs on November 16, 2026; Roybal and Harrington on November 9, 2026. None concerns this petition or its companion litigation.

   `ranged corpus reads: 0 GET(s), 0 byte(s)`

Other shell operations inspected local contract/input files, checked schema shapes and workspace status, and located `apply_patch`; they retrieved no external legal material. One schema-inspection `jq` expression was rejected for invalid `$defs` field syntax and was corrected. Validation uses the same writable uv cache override. No package installation was attempted.

## CourtListener MCP

1. `search(type="o", court="scotus", q='"Exxon Mobil" "CIMEX"', num_results=3)` returned one precedent, Exxon Mobil Corp. v. Corporación Cimex, S.A. (Cuba), docket 24-699, filed June 23, 2026; cluster 10878536, opinion 11346053, official PDF `https://www.supremecourt.gov/opinions/25pdf/24-699_f204.pdf`. This independently corroborated identity/date, not the petition's legal characterization. No own-case search was made.
2. `search_document(opinion_id=11346053, query="recognition", snippet_size=500)` failed with HTTP 502 and returned an error page, not opinion text. Degraded to the corpus and provisioned materials; no direct CourtListener REST request or credential lookup was attempted.

## Web requests

1. A `web.run` call attempted two official-domain searches: `site.supremecourt.gov "Exxon Mobil" "CIMEX" opinion` and `site.supremecourt.gov "Lawrence v. Chater" "reasonable probability"`. The tool returned no usable result content or source references.
2. A `web.run` open request for `https://www.supremecourt.gov/opinions/25pdf/24-699_f204.pdf` likewise returned no usable content. The opinion was not read through this request.

Neither web request sought this petition's disposition, later history, or a forecast. No third-party prediction or own-case outcome surfaced.
