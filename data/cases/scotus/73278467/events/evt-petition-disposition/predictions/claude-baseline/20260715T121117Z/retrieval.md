# Retrieval log — scotus/73278467 / evt-petition-disposition / claude-baseline / 20260715T121117Z

Beyond the provisioned inputs (snapshot 2026-07-15, questions-presented,
petition, brief-in-opposition, event.yaml, context.json) and the committed
`metrics/statpack.md`, I consulted:

## Corpus lookups (`fedcourts query`, ranged backend)

All four queries returned **no rows** (no matching priors surfaced); each
transfer line as reported on stderr:

1. `uv run fedcourts query --court scotus --topic "transgender" --limit 8 --corpus-backend ranged`
   — `ranged corpus reads: 3 GET(s), 786432 byte(s)`
2. `uv run fedcourts query --court scotus --topic "prison" --limit 5 --corpus-backend ranged`
   — `ranged corpus reads: 3 GET(s), 786432 byte(s)`
3. `uv run fedcourts query --court scotus --topic "equal protection" --limit 5 --corpus-backend ranged`
   — `ranged corpus reads: 3 GET(s), 786432 byte(s)`
4. `uv run fedcourts query --court scotus --topic "strip search" --limit 5 --corpus-backend ranged`
   and `--topic "inmate"` — `ranged corpus reads: 3 GET(s), 786432 byte(s)` each

## CourtListener MCP lookups

Purpose: establish the status/holding of the *related* (not this) cases the
petition was evidently held for — Little v. Hecox, No. 24-38, and West
Virginia v. B.P.J., No. 24-43 — which postdate my training data. Forward-mode
cell; no restriction, and none of these touch this case's own outcome (which
does not exist).

1. `search` (opinions, scotus, case_name="Hecox") — 0 results.
2. `search` (opinions, scotus, case_name="B.P.J.") — found West Virginia v.
   B.P.J., decided 2026-06-30, docket 24-43, Kavanaugh, J.
3. `call_endpoint` clusters id=10882186 (metadata only; syllabus field empty).
4. `search` (opinions, B.P.J., restricted fields) ×2 — retrieved the slip
   opinion download URL.

## Web fetch

- `https://www.supremecourt.gov/opinions/25pdf/24-43_2b35.pdf` — the B.P.J.
  slip opinion; extracted the syllabus (first 4 pages only). Holding used:
  sports statutes are sex-based classifications, intermediate scrutiny
  applies, and the laws survive it (Title IX claim also rejected).

No REST fallback used (MCP worked). No lookups touching this case's own
disposition or post-snapshot docket state were made.
