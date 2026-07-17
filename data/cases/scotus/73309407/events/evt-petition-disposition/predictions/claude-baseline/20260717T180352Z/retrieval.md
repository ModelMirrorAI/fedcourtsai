# Retrieval log — scotus/73309407 evt-petition-disposition (claude-baseline, 20260717T180352Z)

## Corpus lookups

- `uv run fedcourts query --court scotus --era modern --limit 8` — **failed**:
  `corpus service at http://127.0.0.1:8377 is unreachable — is the sidecar
  running? (fedcourts corpus-serve): timed out`. No `ranged corpus reads:`
  line was printed (the query never reached the corpus). No further corpus
  queries attempted; fell back to the committed `metrics/statpack.md` for
  base rates per the degradation path in the prompt contract.

## Base rates

- Read committed `metrics/statpack.md`: "Modern discretionary-cert petitions
  by disposition", relist-count, CVSG, originating-court (incl. state
  courts), and per-Term tables. (No salience-band table is present in the
  committed statpack build.)

## CourtListener MCP lookups

- `call_endpoint` `dockets` with `{"id": 73309407}` (fields: id, case_name,
  docket_number, court_id, date_filed, date_terminated, date_last_filing) —
  confirmed the docket is pending (`date_terminated: null`), i.e. the forward
  cell is not mis-provisioned. No other MCP calls.

## Web searches

None.
