# Retrieval — claude-judge, scotus/9526000274, evt-brief-response-disposition, 20260906T174126Z

Beyond the provisioned inputs (event.yaml, outcome.json, record/context.json,
record/documents/application.txt, and the three `record/blinded/<alias>/`
directories):

## Committed statpack

- `metrics/statpack.md`, "The interim docket (applications)" — read to
  check the candidates' 31/296 ≈ 10.5% strictly-prior pool against the
  committed rows (OT2025 17/226, OT2024 14/70; matches) and to describe what
  the harness stamp will pool. Not used to write any rate: on an interim cell
  the baseline and skill are the harness's.

## CourtListener MCP

- `call_endpoint docket-entries {docket: 9526000274}` — HTTP 400, "not one
  of the available choices"; the cell's docket id is not a CourtListener
  docket. No material returned.
- `call_endpoint dockets {id: 9526000274}` — empty result set. No material
  returned.

Both were an attempt to read the application docket's entries for judge
context (the government response's stated position, which two candidates
leaned on). Neither resolved, and I did not pursue it further; the grades do
not turn on it.

## Corpus

No `fedcourts query` / `open-events` lookups.

## Web

No web searches.
