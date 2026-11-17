# Retrieval Log — `gemini-judge` (`scotus/9026000369` / `evt-petition-disposition`)

## 1. Corpus CLI & Statpack Reconstruction (`uv run fedcourts`)

- No `uv run fedcourts query` or `uv run fedcourts open-events` corpus lookups were needed beyond the provisioned case record and statpack history.
- Reconstructed the statpack build in force when each blinded candidate ran (`run_id = 20261031T010306Z`) to verify candidate base-rate citations:
  - `uv run fedcourts statpack-at data/cases/scotus/9026000369/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline` -> resolved `build_sha = 648fc43559f5480348a438523a81df100b5c7301` (`sha256:063aea1961d5833e02e3aa0254477260a34f98f23a2751a1620aaf7c8db03726`).
  - `uv run fedcourts statpack-at data/cases/scotus/9026000369/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline` -> resolved `build_sha = 648fc43559f5480348a438523a81df100b5c7301`.
  - `uv run fedcourts statpack-at data/cases/scotus/9026000369/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline` -> resolved `build_sha = 648fc43559f5480348a438523a81df100b5c7301`.

## 2. CourtListener MCP Lookups

1. `mcp_courtlistener_read_document(opinion_id=11345156, chunk_index=0, chunk_size=8000)`
   - Verified the opening syllabus and holding of *T. M. v. University of Maryland Medical System Corp.*, No. 25-197 (decided June 18, 2026), cited in `petition.txt` and analyzed by `gemini-baseline` and `codex-baseline`.
2. `mcp_courtlistener_read_document(opinion_id=11345156, chunk_index=1, chunk_size=8000)`
   - Verified the remainder of the syllabus and vote/authorship lineup in *T. M. v. University of Maryland Medical System Corp.*, No. 25-197 (June 18, 2026).

## 3. Web Searches

- None performed.
