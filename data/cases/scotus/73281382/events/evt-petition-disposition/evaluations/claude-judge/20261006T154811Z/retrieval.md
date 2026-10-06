# Retrieval log — claude-judge, scotus/73281382, evt-petition-disposition, run 20261006T154811Z

No retrieval beyond the provisioned inputs. Specifically:

- Read the provisioned `event.yaml`, `outcome.json`, `record/context.json`, the `2026-10-05` snapshot, `record/documents/questions-presented.txt` and `documents.json`, and every file under `record/blinded/candidate-{a,b,c}/`.
- Read the committed `metrics/statpack.md` section "Segment base rate by salience band (sal-v4)" for the elevated-band pooled base rate.
- Grepped `docs/salience.md` once to confirm the band lattice's axes (relist count, CVSG, originating circuit, petitioner class), to check a claim in one candidate's reasoning.
- No `fedcourts query` / `open-events` calls (no `ranged corpus reads` lines to record), no CourtListener MCP calls, no web searches.
