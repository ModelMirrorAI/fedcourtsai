# Retrieval log — ca11/68252091 / evt-motion-proceed-ifp / claude-baseline / 20260711T091155Z

## Corpus tooling

- Read the committed `metrics/statpack.md` (overall and by-court base rates).
  The statpack is case-disposition-level (SCOTUS-cert oriented); it has no
  motion-level or IFP-specific cut, so it contributed only weak context (ca11
  resolved rows are sparse: 45 resolved cases).
- `uv run fedcourts query --court ca11 --limit 8`
  - stderr: `ranged corpus reads: 45 GET(s), 11796480 byte(s)`
  - Returned ca11 case-level priors with garbled metadata (mismatched
    summaries/judges, `disposition: other`), none motion-level and none
    relevant to an IFP motion on a mandamus petition. Not used in the
    prediction; noted as a data-quality flag.

## CourtListener MCP

- Attempted `search` (RECAP dockets, party "DeBose", filed before 2024-01-31 —
  petitioner litigation history) → server error: `REDIS_URL is not set; cannot
  access session store.`
- Attempted `search` (ca11 opinions, "DeBose frivolous", filed before
  2024-01-31) → same error.
- The server was down for this cell; no CourtListener data informed this
  prediction. Both attempted queries were date-bounded before the event date
  to avoid surfacing this case's own outcome.

## Web

- None.

Beyond the above, the prediction rests on the provisioned snapshot, the event
definition, and general legal knowledge (28 U.S.C. § 1915, Fed. R. App. P. 24,
Eleventh Circuit IFP/mandamus practice, and unverified general knowledge of the
petitioner's litigation history, discounted in the probability).
