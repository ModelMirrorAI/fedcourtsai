# Retrieval record

## Provisioned and committed materials

Read the prediction contract and prediction schema, the event, case-level context and November 10, 2026 snapshot, documents inventory, questions presented, selected substantive portions of both merits briefs and petitioners' merits reply, the United States' merits amicus, the decision below and lower-court docket supplement, the argument transcript, and its deterministic features. These are the provisioned inputs, not external retrieval. Consulted the guarded merits, complete-lineup, and authorship sections of `metrics/statpack.md`, `metrics/statpack.json`, and their methodology in `metrics/README.md`. JSON aggregation was local; no other prediction or evaluation was read.

## CLI attempts and corpus lookup

1. `uv run fedcourts paths --court scotus --docket 73274853 --event evt-argument-judgment --role predictor` failed before execution because uv's default cache directory was read-only. No case facts were returned.
2. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts paths --court scotus --docket 73274853 --event evt-argument-judgment --role predictor` succeeded and resolved the case/event paths; evaluator-only material was neither named as an input nor opened. The no-sync setting avoided package installation.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --help` displayed structured filters. A later repeat piped through `sed` read the era and cutoff option descriptions. These help calls retrieved no corpus rows.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --citation '440 U.S. 202' --decided-before 2025 --limit 2` attempted a known historic precedent lookup. Result: **no rows**. The CLI explained that only 195 in-scope SCOTUS rows carried any reporter citation and that the filter is sparse; this was treated as missing citation coverage, not absence of the case. No retry through sparse citation filters was made.

   Transfer line, exactly: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`.

## Web attempts

The following general-precedent requests returned no visible results, source text, or usable citation payload, and contributed no facts:

1. Search: `site.supreme.justia.com United States v Bodcaw 440 U.S. 202 1979 attorney fees compensation`.
2. Search: `United States v. Bodcaw 440 U.S. 202 1979`.
3. Open request for the official GovInfo United States Reports PDF, host `www.govinfo.gov`, path `/content/pkg/USREPORTS-440/pdf/USREPORTS-440-202.pdf`.

None requested Hoffmann's disposition, subsequent history, or another forecast.

## CourtListener MCP

1. `search(type="o", citation="594 U.S. 482", num_results=1)` returned **PennEast Pipeline Co. v. New Jersey**, 2021, cluster 4895709, combined opinion 4699488, docket 19-1039. The result reported two matches; only the first was requested and read.
2. `search_document(opinion_id=4699488, query="categorical", snippet_size=800)` returned two passages, one in the syllabus and one in the opinion's discussion of Section 717f(h). Used the latter to check the categorical-delegation language and the discussion of state impediments. This was a limited passage check, not a full reading of PennEast or a ruling on this case's compensation issue.
3. `search(type="o", citation="440 U.S. 202", num_results=1)` returned **United States v. Bodcaw Co.**, cluster/opinion 110026. The result reported five matches; no pagination was requested.
4. `read_document(opinion_id=110026)` returned the full 8,986-character text. Checked the constitutional treatment of ordinary litigation/appraisal expenses, congressional authority to provide additional recovery, and footnote 3 concerning costs assessed against the United States. This supplied substantive precedent context after the empty corpus citation lookup.

## Boundary and limitations

Mode is forward; the shared baseline cutoff is November 10, 2026. No later case-specific material was retrieved. No own-case outcome, subsequent history, or independent forecast surfaced. No provisioned merits text was missing or empty. Empty web responses and sparse corpus citation coverage were worked around through the provisioned record and limited primary-opinion checks. Final CLI validation is a local output check, not retrieval of case facts.
