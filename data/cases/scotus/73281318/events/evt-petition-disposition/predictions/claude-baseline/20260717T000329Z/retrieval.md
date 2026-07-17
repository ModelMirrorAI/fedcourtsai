# Retrieval log — scotus/73281318, evt-petition-disposition, claude-baseline, 20260717T000329Z

Beyond the provisioned inputs (snapshot 2026-07-16, petition, questions
presented, brief in opposition), I consulted:

## Committed base rates

- `metrics/statpack.md` — "Modern discretionary-cert petitions by disposition"
  (grant ≈ 3.1% of resolved), relist-count cuts (0 relists → granted 0.8%),
  CVSG cut (none here), per-Term table (Term 2025 est. grant 2.5%, paid/IFP
  filing split). Note: this statpack revision carries no salience-band table
  and no call-for-response cut.

## Corpus lookups (`fedcourts query`, ranged backend)

1. `uv run fedcourts query --court scotus --citation "547 U.S. 398" --limit 8 --corpus-backend ranged`
   → 0 rows. stderr: `ranged corpus reads: 419 GET(s), 109707264 byte(s)`
2. `uv run fedcourts query --court scotus --topic "criminal" --limit 5 --corpus-backend ranged`
   → 0 rows. stderr: `ranged corpus reads: 3 GET(s), 786432 byte(s)`
3. `uv run fedcourts query --court scotus --limit 5 --corpus-backend ranged`
   → 5 rows (surface sanity check; unrelated recent petitions).
   stderr: `ranged corpus reads: 419 GET(s), 109707264 byte(s)`

The citation/topic filters surfaced no on-point Fourth Amendment cert priors,
so the quantitative anchor is the statpack plus qualitative case-specific
signals (call for response, interlocutory posture, error-correction framing).

## CourtListener MCP / web

None. The provisioned record (full petition with appended lower-court opinion,
full BIO, complete docket proceedings) was sufficient; no MCP or web searches
were made, and no information about this petition's disposition was sought or
encountered.
