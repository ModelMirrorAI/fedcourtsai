# Evaluator Retrieval Log

## Local Statpack / CLI Checks (`fedcourts`)

- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000427 --event evt-petition-disposition --role evaluator`
  - Purpose and result: Confirmed authoritative case, corpus, event, and outcome paths. No corpus query executed.
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts statpack-at data/cases/scotus/9026000427/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts statpack-at data/cases/scotus/9026000427/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts statpack-at data/cases/scotus/9026000427/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
  - Purpose and result: Reconstructed the contemporaneous statpack build in force when all three candidates ran (`build_sha = 7bcde3b105cb212283905eda17b827efc188e80c`, `digest = sha256:84feb6798b6407fea2a17fed92c36d8a8db71d12850a967d840f018295ba4641`, `alternative_sha = null`) and verified each candidate's `sal-v4` and segment base-rate citations against that build.
- Corpus queries (`fedcourts query` / `fedcourts open-events`): None needed.

## CourtListener MCP Lookups

1. `mcp_courtlistener_read_document(opinion_id=759750, chunk_index=[0, 2], chunk_size=8000)`
   - Purpose and result: Read chunks 0 and 2 of *Bosley v. Merit Systems Protection Board*, 162 F.3d 665 (Fed. Cir. 1998) (`23,345` chars total), to verify `codex-baseline`'s characterization of *Bosley*'s holding (affirming dismissal of the continuing paycheck-effect claim based on *Delaware State College v. Ricks*, 449 U.S. 250 (1980), while vacating and remanding on separately alleged post-effective-date reprisals, and predating *Morgan*).

## Web Searches

- None.
