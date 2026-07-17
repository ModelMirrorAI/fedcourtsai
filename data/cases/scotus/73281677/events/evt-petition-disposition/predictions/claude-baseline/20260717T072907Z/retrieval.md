# Retrieval log — scotus/73281677 / evt-petition-disposition / claude-baseline / 20260717T072907Z

Mode: `forward` (retrieval unrestricted).

## Corpus tooling

- `uv run fedcourts query --court scotus --citation "10 U.S.C. § 866" --limit 5`
  → no matching priors returned.
  stderr: `ranged corpus reads: 420 GET(s), 110100480 byte(s)`
- `uv run fedcourts query --court scotus --citation "597 U.S. 1" --limit 5`
  → no matching priors returned.
  stderr: `ranged corpus reads: 420 GET(s), 110100480 byte(s)`
- Read the committed `metrics/statpack.md` for base rates: modern
  discretionary-cert disposition split, per-Term table (Term 2025 grant rate
  2.5%), relist-count cuts (relist-0 ≈ 0.8% granted), CVSG cuts. This
  statpack revision carries no salience-band table.

## CourtListener MCP

- `search(type=d, court=scotus, q="Zhong v. United States", docket_number=25-742)`
  → 0 results (companion petition status check; SCOTUS cert dockets not
  indexed for this search).
- `search(type=d, court=scotus, q="Zhong")` → 0 results.

No other retrieval; the decisive companion-case history (cert denied in
*Schneider*, No. 25-685, and *Dominguez-Garcia*, No. 25-730, both Jan. 12,
2026; *Johnson*, No. 25-682, denied the same day) comes from the provisioned
petition and brief in opposition themselves. No web searches were run, and
nothing retrieved revealed this case's own disposition.
