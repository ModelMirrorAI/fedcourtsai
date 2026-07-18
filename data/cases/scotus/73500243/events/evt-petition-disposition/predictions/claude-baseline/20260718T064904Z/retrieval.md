# Retrieval log — scotus/73500243 · evt-petition-disposition · claude-baseline · 20260718T064904Z

Mode: `forward` (pending petition; unrestricted retrieval per the contract).

## Corpus lookups (`fedcourts`)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8 --corpus-backend service`
   - stderr: `ranged corpus reads: 153 GET(s), 40108032 byte(s)`
   - Used to inspect recent granted priors; all carried `distribution_count` ≥ 3
     (relists), informing the relist-signal adjustment.

## Committed base rates

- `metrics/statpack.md` (+ the per-fee-class detail in `metrics/statpack.json`,
  Term 2025 row): modern discretionary-cert base rates, Term 2025 paid-class
  grant rate ~5.4% / IFP ~1.1%, relist-count cuts (0 relists → 0.8% grant),
  CVSG cut, CA11 originating-circuit cut (~4.4%).

## CourtListener MCP lookups

1. `search` (type=o, court=scotus, q="Zorn v. Linton qualified immunity",
   filed_after=2026-01-01) → 1 hit, cluster 10813527.
2. `get_endpoint_item` clusters/10813527 → *Zorn v. Linton*, per curiam,
   2026-03-23, published.
3. `get_endpoint_item` opinions/11280281 (plain_text) → read the full per
   curiam summary reversal of the Second Circuit QI denial and the Sotomayor
   dissent. Cited in the petition and decided *after* the Eleventh Circuit's
   rehearing denial; used as forward signal on the Court's current appetite
   for QI summary reversals. This is a different case, not this petition's
   disposition — nothing outcome-revealing about 25-1341 was surfaced.

## Web searches

None.
