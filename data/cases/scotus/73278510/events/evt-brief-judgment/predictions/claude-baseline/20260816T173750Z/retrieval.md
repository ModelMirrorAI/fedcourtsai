# Retrieval log

## Corpus tooling

- `uv run fedcourts query --court scotus "Video Privacy Protection Act …"` —
  errored (the command takes no free-text argument, only structured
  filters). No `ranged corpus reads` line was printed. After reading
  `fedcourts query --help`, none of the structured filters (`--court`,
  `--topic`, `--judge`, `--citation`) could target VPPA subject matter on
  SCOTUS rows, so no corpus query was run.
- Base rates: the committed `metrics/statpack.md`, "The merits docket
  (granted cases)" section — pooled disturbed rate 359/515 = 69.7% over
  grant Terms 2017–2024 (strictly before this case's grant Term 2025).

## CourtListener MCP

- `search` (opinions, ca9, VPPA consumer query) — **failed with HTTP 429**:
  the shared daily rate limit (1400/day) was already exhausted, retry
  window ~100 minutes. No CourtListener data was retrieved; no further MCP
  calls attempted.

## Web searches (engine-surfaced, forward mode)

1. `Ninth Circuit VPPA "video tape service provider" consumer subscriber
   decision 2025 newsletter` — surfaced law-firm commentary (natlawreview,
   WilmerHale year-in-review, Law Journal Newsletters, bytebacklaw,
   Troutman, WLF, Finnegan): the Ninth Circuit's March 2025 VPPA decision
   construed "video tape service provider" (movie-theater case), not the
   "consumer" definition at issue here; no Ninth Circuit ruling on the
   consumer question was confirmed.
2. `NBA v. Salazar cert petition 24-994 Supreme Court disposition` —
   surfaced supremecourt.gov docket files for No. 24-994: petition filed
   March 14, 2025, repeatedly distributed (April, October, November 2025),
   supplemental briefs through December 2025, and an indication that
   certiorari was **denied** in late 2025. Used only as vehicle-choice
   context; nothing about this case's own (nonexistent) outcome was sought
   or surfaced.

## Provisioned inputs read

- `record/snapshots/2026-08-16.json` (full docket through Aug 13, 2026)
- `record/documents/questions-presented.txt`
- `record/documents/petition.txt` (cert petition incl. opinions-below
  narrative and split description)
- `record/documents/brief-in-opposition.txt` — carries both the BIO and
  Paramount's June 23, 2026 merits response brief (introduction and
  summary of argument read)
- `record/context.json`, `events/evt-brief-judgment/event.yaml`
