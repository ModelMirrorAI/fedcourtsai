# Retrieval log — scotus/73500220 evt-petition-disposition (claude-baseline, 20260718T064904Z)

## Corpus tooling

- `uv run fedcourts query --court scotus --era modern --limit 5` — **failed**:
  `corpus service at http://127.0.0.1:8377 is unreachable — is the sidecar
  running? (fedcourts corpus-serve): timed out`. No `ranged corpus reads:` line
  was printed (the call never reached the corpus). No further query attempts;
  fell back to the committed statpack.
- Read committed `metrics/statpack.md` for base rates (modern cert disposition
  split, originating-circuit, relist-count, CVSG, and per-Term tables; no
  salience-band table in this statpack version).

## CourtListener MCP

- `search(type=d, court=scotus, case_name="Farhane")` → 0 results.
- `search(type=d, court=scotus, q="Farhane")` → 0 results.
  Purpose: check whether the CA2 en banc *Farhane* decision (the other side of
  the pleaded split) has its own pending SCOTUS proceedings that could make
  this petition a hold/GVR candidate. None found. This case's own disposition
  was never searched for.

## Web searches

None.
