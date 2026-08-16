# Retrieval

## Corpus

- `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`
  - `ranged corpus reads: 25 GET(s), 6553600 byte(s)`
  - Consulted as a loose contemporaneous comparison of observable grant signals, not as a matched-case or outcome lookup.

## Committed base rates

- `metrics/statpack.md` and `metrics/statpack.json`: modern cert disposition, originating-circuit, paid relist, CVSG, per-Term fee-class, and `sal-v3` risk-set cuts.

## CourtListener MCP

- Opinion search: `"Chenery" "ERISA" "plan administrator"`, limited to material filed before August 16, 2026.
- Case searches for `Glista v. Unum Life Insurance Co. of America` and `Susan Card v. Principal Life Insurance Co.`
- Within-opinion searches in `Glista`, 378 F.3d 113, for `newly articulated` and `litigation`.
- Within-opinion searches in `Card`, 17 F.4th 620, for `Chenery`, `rationale`, `private`, and `remand`.

No search targeted this petition's disposition or subsequent history.
