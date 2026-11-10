# Retrieval (claude-judge, 20261110T154355Z)

- No corpus `fedcourts query` / `open-events` calls, no CourtListener MCP lookups, no web searches.
- Ran `uv run fedcourts statpack-at data/cases/scotus/9526000560/record/blinded/<alias>/ --ref origin/main --out-dir /tmp/statpack-at/<alias>` for gemini-baseline, -b, -c. All three resolved to build eb6830084a18 (digest sha256:f6c3af15…, landed 2026-10-19), and I read its interim-docket section to check each candidate's base-rate figures.
- Otherwise only the provisioned inputs: event.yaml, outcome.json, record/context.json, record/blinded/*, record/snapshots/2026-11-09.json, record/opinion/writings.json and writings/OT2026-2/01-per-curiam.txt.
