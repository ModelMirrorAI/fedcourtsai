# Retrieval log

Corpus (`uv run fedcourts query`):

1. `--court scotus --docket-number 26-104` — lead case *Rhoney v. Barbosa da Cunha*: granted 2026-10-01, one distribution. `ranged corpus reads: 21 GET(s), 5505024 byte(s)`
2. `--court scotus --docket-number 25-1415` — *Putra v. Lopez-Campos* (CA6): pending, one distribution (2026-09-28). `ranged corpus reads: 1 GET(s), 262144 byte(s)`
3. `--court scotus --docket-number 26-43` — *Buenrostro-Mendez v. Blanche* (CA5): pending, one distribution (2026-09-28). `ranged corpus reads: 0 GET(s), 0 byte(s)`
4. `--court scotus --disposition gvr --limit 5` — recent GVR rows, for shape only; not used in the number. `ranged corpus reads: 29 GET(s), 7471104 byte(s)`
5. `uv run fedcourts query --help` — usage.

Base rates: `metrics/statpack.md`, "Segment base rate by salience band (sal-v8)", federal column; `cert_anchor` in `record/context.json`.

Web search (one, standard mode): "Rhoney v. Barbosa da Cunha Supreme Court 26-104 certiorari granted 1225(b)(2)(A) argument". It confirmed the October 1, 2026 grant and the question presented, and reported that argument is expected in late February or early March 2027 (ACLU case page; unconfirmed by a calendar entry). No forecast of this case or the lead case surfaced.

CourtListener MCP: not used.
