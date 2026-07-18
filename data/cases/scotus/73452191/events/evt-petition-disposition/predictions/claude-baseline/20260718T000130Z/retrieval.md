# Retrieval log — scotus/73452191 / evt-petition-disposition / claude-baseline / 20260718T000130Z

Beyond the provisioned inputs (snapshot 2026-07-17, `questions-presented.txt`,
`petition.txt`, `documents.json`) and the committed `metrics/statpack.md`:

## Corpus lookups

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   - stderr: `ranged corpus reads: 149 GET(s), 39059456 byte(s)`
   - Purpose: profile what recent granted petitions look like on the docket
     (distribution counts, salience, counsel). Takeaway: recent grants
     typically show multiple distributions/relists and often repeat-player
     counsel; this petition has zero distributions beyond its initial one.

## CourtListener MCP lookups (mode: forward — unrestricted)

2. `search(type=d, court=scotus, q="Goldston")` — checked whether the Fourth
   Circuit companion split case (*Gibson v. Goldston*) produced a SCOTUS cert
   petition whose fate would be forward signal. Result: 0 dockets indexed.
3. `search(type=d, court=scotus, q="Eighmy")` — same check for *Rockett v.
   Eighmy*. Result: HTTP 429 (shared daily rate limit exhausted); not
   retried. Retrieval stopped here and the prediction rests on the
   provisioned inputs, the statpack, and lookup (1)–(2).

No web searches were used. Nothing retrieved concerned this case's own
disposition (none exists yet — the petition is pending, conference set for
2026-09-28).
