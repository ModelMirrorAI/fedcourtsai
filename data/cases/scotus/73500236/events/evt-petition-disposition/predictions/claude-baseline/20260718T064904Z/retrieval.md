# Retrieval log — scotus/73500236 / evt-petition-disposition / claude-baseline / 20260718T064904Z

Mode: `forward` (retrieval unrestricted; the petition is pending —
distributed for the 9/28/2026 conference, after the snapshot date).

## Corpus tooling

- `uv run fedcourts query --court scotus --era 2020s --limit 8` — **failed**:
  `corpus service at http://127.0.0.1:8377 is unreachable — is the sidecar
  running? (fedcourts corpus-serve): timed out`. No `ranged corpus reads:`
  line was printed (the command never reached the corpus).
- Retried the same command once — same timeout. Proceeded without corpus
  priors.
- Base rates taken from the committed `metrics/statpack.md` and the
  per-fee-class detail in `metrics/statpack.json` (Term 2025/2024 paid vs.
  IFP grant rates; relist and CVSG cuts).

## CourtListener MCP

- `search(type=d, court=scotus, q="Landmark Towers" OR "Marin Metropolitan")`
  — 0 results (SCOTUS dockets for the prior round are not in the search
  index under those terms).
- `search(type=o, q="Landmark Towers" "UMB Bank")` — found the related
  litigation chain, including *UMB Bank, N.A. v. Landmark Towers Ass'n,
  Inc.*, No. 19-241 (U.S. Nov. 25, 2019), 140 S. Ct. 566 — the cert
  **denial** in the prior round of this same district's bond dispute. Used
  as forward signal (public information predating the snapshot). No lookup
  touched this petition's own disposition, which does not yet exist.

## Web searches

None.
