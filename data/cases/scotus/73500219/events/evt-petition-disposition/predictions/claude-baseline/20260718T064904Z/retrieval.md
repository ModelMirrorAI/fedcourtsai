# Retrieval log — scotus/73500219 · evt-petition-disposition · claude-baseline · 20260718T064904Z

Mode: `forward` (pending petition; conference 9/28/2026 postdates this run).
Nothing outcome-revealing was sought or surfaced — the disposition does not
exist yet.

## Corpus lookups (`fedcourts`)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 6`
   - stderr: `ranged corpus reads: 153 GET(s), 40108032 byte(s)`
   - Purpose: profile recent SCOTUS cert grants for pre-grant docket signals.
     All six granted priors carried multiple distributions (3, 3, 4, 4, 17, 22),
     corroborating the statpack's relist-bucket gradient; this petition has a
     single distribution so far.

## CourtListener MCP lookups

1. `search(type="d", court="scotus", q="Maund")` — 0 results. CourtListener
   carries no docket for this petition or its companions; no further docket
   detail available there.
2. `search(type="o", court="scotus", q="\"Remmer\" \"extraneous\"", filed_after=2015-01-01)`
   — 1 result: *Dietz v. Bouldin* (2016). Purpose: check for recent merits
   engagement or dissents from denial on the Remmer prejudice standard; none
   found on point, supporting the percolation/denial prior.

## Committed artifacts

- `metrics/statpack.md` and `metrics/statpack.json` — modern discretionary-cert
  base rates: Term-2025 overall ~2.5% grant, paid class ~5.4%, CA6-originating
  ~3.5%, relist-0 ~0.8%, no-CVSG ~3.0%. (The salience-band table referenced in
  the predict prompt is not present in the committed statpack; noted in
  `tooling.json`.)

No web searches were run.
