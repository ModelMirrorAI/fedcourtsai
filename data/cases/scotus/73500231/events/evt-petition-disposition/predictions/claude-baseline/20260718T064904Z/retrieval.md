# Retrieval log — scotus/73500231 / evt-petition-disposition / claude-baseline / 20260718T064904Z

## Corpus lookups

- `uv run fedcourts query --court scotus --era 2020s --limit 5` — **failed**:
  `corpus service at http://127.0.0.1:8377 is unreachable — is the sidecar
  running? (fedcourts corpus-serve): timed out`. No `ranged corpus reads:` line
  was printed (the query never reached the corpus). No further corpus queries
  attempted; fell back to the committed `metrics/statpack.md` for base rates.

## Base rates

- Read the committed `metrics/statpack.md`: "Modern discretionary-cert
  petitions by disposition", "Modern cert petitions by originating circuit"
  (cadc row), "Cert petitions by relist count" (0-relist bucket), "Cert
  petitions by CVSG status", and the "SCOTUS cert petitions by Term" table
  (Term 2025 row: est. grant rate 2.5%). No "Segment base rate by salience
  band" table is present in the committed statpack version.

## CourtListener MCP lookups (forward mode — unrestricted)

1. `search(type=d, q="Drevaleva", court=scotus)` — 0 docket results.
2. `search(type=o, q="Drevaleva")` — 11 opinion/order results, including eight
   prior Drevaleva Supreme Court docket entries from 2019–2020 (Nos. 18-8315,
   18-8746, 18-8764, 18-8919, 18-9249, 18-9250, 19-6631, 19-8012) plus related
   lower-court litigation (dcd 2024-cv-1023). Used solely as petitioner
   litigation-history context; nothing about this petition's own (pending)
   disposition was sought or surfaced.

## Web searches

None.
