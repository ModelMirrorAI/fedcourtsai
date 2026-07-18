# Retrieval log — scotus/73500216 evt-petition-disposition claude-baseline 20260718T064904Z

Mode: `forward` (`record/context.json`).

## Provisioned inputs read

- `record/snapshots/2026-07-18.json` (baseline snapshot)
- `record/documents/questions-presented.txt`
- `record/documents/petition.txt` (89 pp., full text; no BIO was provisioned —
  none has been filed per the snapshot)
- `record/documents/documents.json`
- `events/evt-petition-disposition/event.yaml`
- `metrics/statpack.md` (committed base rates: per-Term, relist, CVSG,
  originating-circuit cuts; this statpack carries no salience-band table)

## Corpus lookups

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted`
   - stderr: `ranged corpus reads: 153 GET(s), 40108032 byte(s)`
   - Purpose: characterize recently granted petitions in the selected slice to
     compare this case's signals (counsel, amici, CVSG, relists) against the
     granted pool. Result: grants dominated by elite counsel, amici, CVSG, and
     multi-distribution dockets — none present here.

## CourtListener MCP lookups

1. `call_endpoint dockets {id: 73500216, fields: id,case_name,docket_number,court_id,date_filed,date_terminated,date_last_filing}`
   - Purpose: confirm the forward cell is properly provisioned (case still
     pending). Result: `date_terminated: null` — pending; no outcome surfaced.

## Web searches

None.
