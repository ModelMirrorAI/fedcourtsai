# Retrieval — claude-judge, run 20261110T154355Z

No corpus queries, CourtListener lookups or web searches.

- `uv run fedcourts statpack-at data/cases/scotus/73522552/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`. This rebuilt the statpack build the candidates were placed against (7bcde3b105cb, digest sha256:84feb679…, alternative_sha null) to check the base-rate figures. It reads only the statpack history.
- Local reads of provisioned inputs only: event.yaml, outcome.json, record/context.json, record/snapshots/2026-11-09.json, record/documents/petition.txt (grep for cited denials), the start of brief-in-opposition.txt, and the blinded candidate directories.
