# Retrieval Log — `gemini-judge` (`20261117T154407Z`)

No corpus queries (`uv run fedcourts query` / `open-events`), CourtListener MCP calls, or web searches/fetches were performed beyond the provisioned inputs.

To verify the candidates' base-rate citations against the statpack build in force when they ran (`20261109T212928Z`, `sha256:9da7dbfa464075bfc7fab6e6b641ec9060684cd53259a76380a32823adf6f653`), reconstructed that statpack from local git history (`ca0c9e1a49e292692bdc5b092cd9f868561169b8`) into scratch outside the repository via:

- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts statpack-at data/cases/scotus/73500225/record/blinded/gemini-baseline/ --ref origin/main --out-dir /home/runner/.gemini/tmp/fedcourtsai/statpack-at/gemini-baseline`
