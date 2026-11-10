# Retrieval — claude-judge, scotus/73522552, evt-petition-disposition, run 20261110T154355Z

No retrieval beyond the provisioned inputs, apart from one statpack rebuild to check gemini-baseline's base-rate figure:

- `uv run fedcourts statpack-at data/cases/scotus/73522552/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline` → build 1c4f550b7b75 (digest sha256:6686e969…, alternative_sha null). I read the sal-v4 band table from it. No `fedcourts query`, no CourtListener MCP, no web.
