# Retrieval log

No corpus query, CourtListener lookup or web search was made.

- `uv run fedcourts statpack-at data/cases/scotus/9526000657/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline` - rebuilt the statpack build the candidates recorded (`statpack_digest` sha256:b122cc43..., build f0a8cabd41e6, landed 2026-11-07, no alternative). All three candidates carry the same digest, so this one build served for all of them. Reads only statpack history; no `ranged corpus reads` line.
- Provisioned inputs read: event.yaml, outcome.json, record/context.json, the 2026-11-12 snapshot, record/documents/application.txt (table of contents and a keyword scan only), the case summaries, and each candidate's staged files.
