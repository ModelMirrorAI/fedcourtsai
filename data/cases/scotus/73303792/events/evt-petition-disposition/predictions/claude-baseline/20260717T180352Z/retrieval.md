# Retrieval log — scotus/73303792 / evt-petition-disposition / claude-baseline / 20260717T180352Z

## Corpus tooling

- `uv run fedcourts query --court scotus --era modern --limit 8` — **failed**:
  `corpus service at http://127.0.0.1:8377 is unreachable — is the sidecar
  running? (fedcourts corpus-serve): timed out`. No `ranged corpus reads` line
  was printed (the query never reached the corpus). No further corpus queries
  attempted; fell back to the committed statpack.
- Read the committed `metrics/statpack.md` for base rates (modern
  discretionary-cert disposition split, relist-count buckets, CVSG buckets,
  originating-circuit table, per-Term table). The statpack in this checkout has
  no "Segment base rate by salience band" section.

## CourtListener MCP (forward mode — unrestricted; 5 calls)

1. `search(type=o, court=ca6, docket_number=24-3840)` — 0 results (the Sixth
   Circuit decision below is not in the opinion index).
2. `search(type=o, court=ca6, case_name="Gomez v. Ryan")` — 0 results.
3. `search(type=d, court=ca6, docket_number=24-3840)` — 1 result: docket
   69636140, "John Gomez v. David Ryan," parties John Gomez / David Ryan; no
   nature-of-suit, cause, or date fields populated.
4. `call_endpoint(dockets, id=69636140)` — sparse record; no
   appeal-from, panel, nature-of-suit, or date fields populated.
5. `search(type=o, court=ca6, q=Gomez, filed 2025-11-01..2025-12-31)` — 5
   results, none this case (confirms the Dec 2, 2025 disposition below was an
   unpublished/uningested order).

One additional exploratory docket search (`type=d`, courts ohsd/ohnd,
q="Gomez Ryan") returned no matching district-court docket for this
litigation. No search surfaced this petition's own disposition (the case is
pending; distributed for the 2026-09-28 conference).

## Web searches

None.
