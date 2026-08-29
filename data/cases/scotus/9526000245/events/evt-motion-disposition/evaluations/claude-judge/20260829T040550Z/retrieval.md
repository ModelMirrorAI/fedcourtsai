# Retrieval — claude-judge, evt-motion-disposition, run 20260829T040550Z

Beyond the provisioned inputs (event.yaml, outcome.json, the blinded
candidate directories, record/context.json):

## Committed statpack

- Read `metrics/statpack.md`, "The interim docket (applications)" (grep for
  the section, then the table) — to state for the reader what the
  harness-stamped interim baseline should pool: strictly-prior OT2025
  (16/178) + OT2024 (14/49) = 30/227 ≈ 13.2%, above the 50-resolved floor.
  The baseline itself is stamped by the harness on an interim cell, not
  written here.

## CourtListener MCP

- `call_endpoint` (`parties`, docket 73658638, fields name/party_types) —
  one lookup to check gemini-baseline's characterization of the respondent
  against the district party record while grading its reasoning quality
  (context for scoring an existing claim, not new case facts). The record
  lists the applicants pro se and Gerol among a respondent group tied to a
  Washington County court.

## Corpus (`fedcourts query` / `open-events`)

- Not used; no `ranged corpus reads` lines to report.

## Web

- None.
