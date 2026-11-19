No corpus, CourtListener MCP, or web lookup was made by this evaluator. Case facts and forecast checks use only the provisioned outcome, docket snapshot, briefs and blinded candidate inputs. The absent opinion/writings slots were not supplemented externally.

Base-rate provenance was checked using the prompt-authorized statpack-history reconstruction, once for each alias:

- `UV_CACHE_DIR=/tmp/fedcourts-eval-uv uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000100/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
- `UV_CACHE_DIR=/tmp/fedcourts-eval-uv uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000100/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
- `UV_CACHE_DIR=/tmp/fedcourts-eval-uv uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000100/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`

All succeeded and selected build `eb6830084a187953fd58b91cb3c9125fc6775a7b`, landed October 19, 2026, digest `sha256:f6c3af155898c161beb3ba174781949a02784094085267d79a074680a859b1ba`, with no alternative. Read the reconstructed statpack's relevant cert and segment tables and corresponding prior-Term baseline fields. These commands consult statpack history, not prediction history or the corpus, and emit no ranged-corpus transfer line. Initial invocations with uv's default cache failed before execution because that cache is read-only; the /tmp override resolved it without installing anything.
