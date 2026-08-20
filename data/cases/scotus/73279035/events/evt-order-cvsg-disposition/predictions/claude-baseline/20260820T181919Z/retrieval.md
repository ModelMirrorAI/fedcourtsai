# Retrieval log

## Corpus (`fedcourts query`) — both attempts failed, no rows retrieved

1. `uv run fedcourts query --court scotus --citation "563 U.S. 421"`
   - stderr: `corpus service at http://127.0.0.1:8377 timed out after 180s — a slow corpus read, not a dead sidecar: ReadTimeout('timed out')`
   - No `ranged corpus reads:` line was printed (the read never completed); no rows returned.
2. `timeout 100 uv run fedcourts query --court scotus --disposition granted --era modern --limit 5`
   - Killed by the 100s timeout wrapper before producing output; no `ranged corpus reads:` line, no rows.

No corpus priors inform this prediction; base-rate context came from the
committed `metrics/statpack.md` instead (the modern-cert disposition section,
the CVSG-status cut, the relist-count cut, and the sal-v3 segment
base-rate-by-band table pooled over OT2017–OT2024).

## CourtListener MCP (3 calls)

1. `search` (dockets, court=scotus, q="Aramark Aetna") — 0 results: no SCOTUS
   cert petition from the Fifth Circuit's Aramark litigation in the RECAP index.
2. `search` (opinions, court=ca5, q=`surcharge "502(a)(3)" equitable relief
   fiduciary`, filed after 2025-01-01) — 1 result: *Aramark Services v. Aetna
   Life Ins*, CA5 No. 24-40323, dateFiled 2025-12-18 — confirms the decision
   the BIO builds its "await a fiduciary vehicle" argument on.
3. `search` (dockets, court=scotus, q=`"Rose" "PSA Airlines"`) — 0 results: the
   prior petition on this QP (No. 23-734, distinguished in the petition) is not
   in the RECAP SCOTUS index; its history is carried only as hedged
   training-knowledge context in `reasoning.md`.

## Web searches

None.
