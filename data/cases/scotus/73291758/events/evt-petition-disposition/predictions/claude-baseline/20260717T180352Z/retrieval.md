# Retrieval log — scotus/73291758 / evt-petition-disposition / claude-baseline / 20260717T180352Z

Mode: `forward` (record/context.json).

## Corpus tooling

- `uv run fedcourts query --court scotus --era 2020s --limit 8` — **failed**:
  `corpus service at http://127.0.0.1:8377 is unreachable — is the sidecar
  running? (fedcourts corpus-serve): timed out`. No `ranged corpus reads:`
  line was printed (the call never reached the corpus). No further `fedcourts
  query` calls attempted; fell back to the committed statpack per the
  degrade-gracefully rule.
- Read the committed `metrics/statpack.md` (and inspected
  `metrics/statpack.json` for the per-fee-class Term detail) for base rates:
  modern discretionary-cert disposition split, relist-count buckets, CVSG
  buckets, originating-court table, Term 2025 paid/IFP grant rates. Note: the
  "Segment base rate by salience band" table named in the prompt is not
  present in this statpack build.

## CourtListener MCP

- `call_endpoint` `dockets` `{"id": 73291758}` — one lookup to confirm
  current docket state: case pending (no `date_terminated`, no
  `date_cert_granted`/`date_cert_denied`), docket 25-1245, filed 2026-05-04,
  originating judgment 2025-09-18 (Appellate Court of Illinois, First
  District). Forward-mode status check; surfaced no disposition (none
  exists).

## Web searches

None.
