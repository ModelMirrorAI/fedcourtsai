# Evaluator Retrieval Log (`gemini-judge`, run `20261117T154407Z`)

## Historical Statpack Reconstruction (`fedcourts statpack-at`)

- `uv run fedcourts statpack-at data/cases/scotus/9026000372/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
  - Resolved `run_id: 20261031T173439Z` (`cert_anchor` digest `sha256:a059cb872f890b63515d8e2ac6ef798347ae7231a62d08543a5b7431bd941faa`) to `build_sha: dedb32b153e67d254af10083c3ee247cecd56116` (`landed_at: 2026-10-31T10:28:26-04:00`, `alternative_sha: null`).
- `uv run fedcourts statpack-at data/cases/scotus/9026000372/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
  - Resolved to the same `build_sha: dedb32b153e67d254af10083c3ee247cecd56116` (`sha256:a059cb872f890b63515d8e2ac6ef798347ae7231a62d08543a5b7431bd941faa`).
- `uv run fedcourts statpack-at data/cases/scotus/9026000372/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`
  - Resolved to the same `build_sha: dedb32b153e67d254af10083c3ee247cecd56116` (`sha256:a059cb872f890b63515d8e2ac6ef798347ae7231a62d08543a5b7431bd941faa`).

## Corpus CLI Lookups (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number 19-764`
   - Transfer line: `ranged corpus reads: 21 GET(s), 5505024 byte(s)`
   - Verified `scotus/66728171` (*Mark I. Sokolow, et al. v. Palestine Liberation Organization, et al.*, No. 19-764, `disposition: gvr`, `date_cert_granted: 2020-04-27`).
2. `uv run fedcourts query --court scotus --docket-number 24-20`
   - Transfer line: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Verified `scotus/69830688` (*Miriam Fuld, et al. v. Palestine Liberation Organization, et al.*, No. 24-20, `disposition: granted`, `merits_decided: 2025-06-20`, `merits_judgment: reversed`).
3. `uv run fedcourts query --court scotus --docket-number 24-151`
   - Transfer line: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Verified `scotus/72483856` (*United States v. Palestine Liberation Organization, et al.*, No. 24-151, `disposition: granted`, `merits_decided: 2025-06-20`, `merits_judgment: reversed`).
4. `uv run fedcourts query --court scotus --docket-number 26A141`
   - Transfer line: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Verified `scotus/9526000141` (*Palestine Liberation Organization, et al. Applicants v. Mark I. Sokolow, et al.*, No. 26A141, filed `2026-07-30`, decided `2026-08-03`, `disposition: denied`, `response_requested: false`, `referred_to_court: false`).

## CourtListener MCP Lookups

- None (all lower-court and Supreme Court context needed to verify the candidates' analyses was present in the provisioned `petition.txt`, `appendix.txt`, snapshots, and corpus rows).

## Web Searches

- None.
