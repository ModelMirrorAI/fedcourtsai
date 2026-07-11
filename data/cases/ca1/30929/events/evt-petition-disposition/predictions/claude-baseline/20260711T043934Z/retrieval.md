# Retrieval log — ca1/30929 evt-petition-disposition (claude-baseline, 20260711T043934Z)

## Corpus lookups (`fedcourts`, ranged backend)

1. `uv run fedcourts query --court ca1 --corpus-backend ranged --limit 8`
   - `ranged corpus reads: 27 GET(s), 7077888 byte(s)`
   - Returned 8 resolved ca1 priors, all disposition `other`; attached opinion
     text/summaries were mismatched (unrelated historical state-court material),
     so only the disposition labels were usable.
2. `uv run fedcourts query --court ca1 --topic "3440 Other Civil Rights" --corpus-backend ranged --limit 10`
   - `ranged corpus reads: 258 GET(s), 67633152 byte(s)`
   - One resolved prior (ca1/4680, 18-1898, decided 2019-06-27), disposition `other`.

## Base rates

- Read the committed `metrics/statpack.md`: overall base rate and the
  "Cases by court" ca1 row (resolved: other 86.3%, dismissed 8.0%, denied 5.0%,
  granted 0.7%).

## CourtListener MCP

- Attempted 2 calls (RECAP search for the originating D.P.R. docket
  3:18-cv-01993, entries capped at the 2020-03-24 event date; then a
  docket-level retry). Both failed with a server-side error: `REDIS_URL is not
  set; cannot access session store.` No CourtListener data informed this
  prediction.

## Not retrieved, deliberately

- This case's post-event docket entries (how the show-cause proceeding or the
  appeal resolved), per the never-retrieve-this-case's-outcome rule.
- Cluster 195546 linked on the docket: the docket's `date_created` (2014)
  predates this 2019 appeal, so the linked cluster is likely a merge artifact
  from an unrelated case, and if it were not, opening it could reveal this
  appeal's outcome.

No web searches were used.
