# Retrieval record

## Local materials beyond the provisioned case inputs

- Read the task contract, repository instructions, prediction schema, and tooling/flags schemas.
- Read the modern-cert disposition, originating-circuit, paid relist, paid CVSG, salience-band, and prior-Term reached-rate sections of `metrics/statpack.md`.
- Inspected aggregate `metrics/statpack.json` structure and computed the `sal-v4` high-band reached-rate pool over displayed Terms 2017–2024: 314 weighted grants / 898 weighted resolved petitions. No case-level outcome records were consulted.
- Ran `uv run fedcourts paths --court scotus --docket 73281057 --event evt-order-cvsg-disposition --role predictor`. The first invocation failed because the default uv cache was read-only; retrying with `UV_CACHE_DIR=/tmp/uv-cache` succeeded. This resolves paths and does not query corpus priors.
- No `fedcourts query` or `open-events` calls; consequently no ranged-corpus-read transfer lines were generated.

## CourtListener MCP

1. `search(type="o", court="ca9", docket_number="24-1570", filed_after="2025-08-25", filed_before="2025-08-27", num_results=3)`. One result: Pharmaceutical Research and Manufacturers of America v. Stolfi, August 26, 2025; cluster 10660891, opinion 11127478. This is the pre-petition lower-court opinion, not the Supreme Court event's disposition.
2. `search_document(opinion_id=11127478, query="Philip Morris", snippet_size=1400)`. Result: no text available. No substantive opinion passage was retrieved and no direct CourtListener REST fallback was attempted.

## Web attempts

1. Searched `site.law.cornell.edu rules supct rule 10 considerations governing review certiorari` for general review criteria, not this case. The tool returned no usable results.
2. Attempted to open Cornell's `/rules/supct/rule_10` page. The tool returned no usable text. No web-derived legal proposition was used.

No search sought this petition's Supreme Court disposition or later history. No outcome-revealing material surfaced.
