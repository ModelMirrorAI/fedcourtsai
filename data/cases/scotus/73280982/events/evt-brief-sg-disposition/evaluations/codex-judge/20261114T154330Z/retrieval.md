# Evaluator retrieval record

Read only the evaluation contract, output schemas, blinded candidate files, the provisioned event/outcome, case context, November 14 docket snapshot, document manifest and relevant provisioned filings, plus repository tooling metadata and committed statpack context. No candidate identity lookup, prediction-history read, corpus query, CourtListener lookup, web search, external order retrieval or external opinion retrieval was performed.

Reconstructed each candidate's historical base-rate inputs with the contract's allowed statpack-only history lookup:

- `UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts statpack-at data/cases/scotus/73280982/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
- `PYTHONDONTWRITEBYTECODE=1 UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts statpack-at data/cases/scotus/73280982/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
- `PYTHONDONTWRITEBYTECODE=1 UV_NO_SYNC=1 UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts statpack-at data/cases/scotus/73280982/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`

All three succeeded, resolving prediction run `20261026T092709Z` to build `eb6830084a187953fd58b91cb3c9125fc6775a7b`, landed October 19, 2026, digest `sha256:f6c3af155898c161beb3ba174781949a02784094085267d79a074680a859b1ba`. None recorded its own digest; the helper selected the historical build by run time, with no alternative build reported. Read its CVSG section and sal-v4 per-Term band table to assess candidates' use of their contemporaneous pack, not to generate a new scoring baseline. These local-history commands emit no ranged-corpus transfer line.

codex-baseline's own retrieval note reports precedent research not present in its staged log. That is evidence reviewed for the leakage assessment, not retrieval performed by this evaluator; the resulting audit limitation is in flags.json.

Validation uses the already-installed system Python jsonschema implementation against the three named output schemas, and the repository's installed Pydantic models. No package was installed and no whole-tree validation was run.
