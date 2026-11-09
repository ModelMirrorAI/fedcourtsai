# Evaluator retrieval

Read the provisioned event, outcome, current context and docket snapshot, document manifest, questions presented, relevant petition and opposition passages, the staged supplemental brief, and every blinded candidate's prediction, rationale, forecast, retrieval note, and captured retrieval log. No external case facts, orders, opinions, or commentary were retrieved. No corpus query, open-events call, CourtListener lookup, or web search was made.

Read the committed `metrics/statpack.md` for aggregate context. To check each candidate's base-rate reasoning against the build available at prediction time, ran:

```text
UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/73520108/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline
UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/73520108/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline
UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/73520108/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline
```

Each succeeded and recovered build `1c4f550b7b758c0f5dbb4d505b8159cd8e93fee5`, landed September 28, 2026, with digest `sha256:6686e96900da7521a4a61b621aa78c4a04231c24a834f547cd36848f501f675e` and no alternative build. Inspected that build's sal-v4 prior-Term risk-set table and matching JSON inputs. These commands consult statpack-only repository history, not candidate identity or prediction history; they print no ranged-corpus transfer line. No hand-pooled scoring baseline or skill was written.
