# Retrieval log

## Corpus lookups

- `uv run fedcourts query --court ca11 --corpus-backend ranged --limit 10`
  — stderr: `ranged corpus reads: 45 GET(s), 11796480 byte(s)`. Returned the
  ca11 resolved priors (mostly historical, low relevance to a modern pro se
  mandamus petition; none used directly).
- Read the committed `metrics/statpack.md` for base rates (ca11 cut: 45
  resolved, other 95.6% / denied 2.2% / granted 2.2% — too small and too
  historical to anchor on).

## CourtListener MCP

Unavailable this run: every call (`search`, `call_endpoint`) failed with
`REDIS_URL is not set; cannot access session store` (server-side session-store
misconfiguration). Attempted lookups (all failed, no data retrieved):

- RECAP docket search for the underlying district case, flnd 4:22-cv-00439 (×2)
- `call_endpoint` `dockets` for flnd 4:22-cv-00439

## Web searches

- WebSearch: `DeBose "4:22-cv-00439" Northern District of Florida complaint`
  — identified the underlying case as *DeBose v. University of South Florida
  Board of Trustees* (N.D. Fla., filed 2022-12-08) and the magistrate judge's
  recommendation to dismiss under 28 U.S.C. § 1406(a) for improper venue
  because the plaintiff acted to intentionally circumvent an injunction order.
  Source: [CourtListener docket 66624381](https://www.courtlistener.com/docket/66624381/debose-v-the-university-of-south-florida-board-of-trustees/).
  The result did not mention this mandamus petition's disposition, and I did
  not search for it.
