# Retrieval log — ca1/30929 evt-appeal-disposition (claude-baseline, 20260711T043934Z)

## Corpus lookups (`fedcourts`, ranged backend)

1. `uv run fedcourts query --court ca1 --topic "3440 Other Civil Rights" --corpus-backend ranged --limit 8`
   - stderr: `ranged corpus reads: 258 GET(s), 67633152 byte(s)`
   - Returned one prior (ca1/4680, "18-1898", disposition `other`), whose
     attached summary text is plainly from an early-1900s Missouri state
     case — a mislabeled corpus row; noted in tooling/flags, not relied on.
2. `uv run fedcourts query --court ca1 --era 2010s --limit 6 --corpus-backend ranged`
   - stderr: `ranged corpus reads: 27 GET(s), 7077888 byte(s)`
   - Six modern CA1 priors, every resolved one labeled `other` — consistent
     with the statpack's CA1 label distribution.

## Base rates

- Read the committed `metrics/statpack.md` (CA1 resolved base rate: other
  86.3%, dismissed 8.0%, denied 5.0%, granted 0.7%).

## CourtListener MCP

- None. This is a `forward` cell, but the snapshot's docket data is six years
  stale; a live read of this docket would likely reveal the realized
  disposition, so I skipped MCP retrieval entirely to honor the
  never-retrieve-this-case's-outcome rule.

## Web searches

- None.
