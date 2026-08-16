# Retrieval log

Beyond the provisioned inputs (snapshot `record/snapshots/2026-08-16.json`;
`record/documents/`: `petition.txt`, `questions-presented.txt`,
`brief-in-opposition.txt` — the last containing both the BIO and the
respondents' merits brief of Jul 27, 2026; the committed `metrics/statpack.md`
merits section):

## Corpus lookups

- `uv run fedcourts query --court scotus --citation "564 U.S. 410" --citation "479 U.S. 481" --limit 5`
  — no rows returned.
  stderr: `ranged corpus reads: 1329 GET(s), 348389376 byte(s)`
  and `note: citations filter: 161 of 590339 rows in scope (scotus) carry
  citation data, and the column holds a case's OWN reporter cites (not a
  cases-citing-this-authority graph) — an empty result here usually means
  missing data, not no match`.

## Web searches (engine-surfaced, forward mode)

- `Suncor Exxon Boulder certiorari granted 25-170 jurisdiction question Supreme Court February 2026`
  — confirmed the 2026-02-23 grant and the Court-added jurisdictional question
  (SCOTUSblog case page, law-firm client alerts).
- `Suncor Boulder 25-170 Supreme Court Alito recusal "took no part" grant`
  — confirmed Justice Alito did **not** recuse at the grant (no
  non-participation notation in the Feb 23, 2026 order), unlike the 2023
  Boulder petition (press coverage of the recusal reversal).

No CourtListener MCP calls were made. Neither web search surfaced any
disposition of this case — the case is pending, argument set for
October 5, 2026.
