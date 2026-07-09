# Retrieval log — scotus/1061793 / evt-petition-disposition / claude-baseline / 20260709T162611Z

Beyond the provisioned snapshot and event definition, this run consulted:

## Committed base rates

- `metrics/statpack.md` — corpus-wide and SCOTUS base rates (SCOTUS resolved:
  other 78.4%, dismissed 15.9%, denied 4.4%, granted 1.4%). The "Modern
  discretionary-cert petitions by disposition" section the predict prompt
  points at is not present in the committed statpack (flagged in
  `flags.json`); this case has no Term-prefixed docket number, so the era
  cuts were the relevant anchor anyway.

## Corpus lookups (`fedcourts`, ranged backend)

1. `uv run fedcourts query --court scotus --era 1990s --limit 8 --corpus-backend ranged`
   - `ranged corpus reads: 378 GET(s), 99090432 byte(s)`
   - Returned 8 resolved 1990s SCOTUS priors (mostly disposition `other`,
     one `denied`); none factually comparable. Run twice (second pass only
     reformatted the same result set; it reported the same ranged-reads
     line).
2. `uv run fedcourts query --court scotus --citation "410 U.S. 113" --citation "505 U.S. 833" --era 1990s --limit 5 --corpus-backend ranged`
   - `ranged corpus reads: 378 GET(s), 99090432 byte(s)`
   - Returned zero rows: no resolved 1990s SCOTUS priors in the corpus cite
     Roe or Casey.

## Not consulted

- No CourtListener MCP lookups. The linked opinion cluster on this docket
  was deliberately **not** opened: for this case it is the disposition
  itself, which the contract forbids retrieving.
- No web searches.
- Note: I recognized this case from general legal knowledge, including its
  outcome — disclosed in `reasoning.md` and flagged in `flags.json`.
