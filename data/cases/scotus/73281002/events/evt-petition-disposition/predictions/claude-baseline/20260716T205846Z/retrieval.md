# Retrieval log — scotus/73281002 evt-petition-disposition (claude-baseline, 20260716T205846Z)

Mode: `forward` (`record/context.json`), so retrieval was unrestricted. The case
is pending a CVSG response (invited June 29, 2026); no disposition exists to leak.

## Corpus lookups (`fedcourts`, ranged backend)

1. `uv run fedcourts query --court scotus --topic "election law" --corpus-backend ranged`
   - stderr: `ranged corpus reads: 3 GET(s), 786432 byte(s)`
   - 0 rows returned.
2. `uv run fedcourts query --court scotus --citation "504 U.S. 428" --citation "460 U.S. 780" --citation "553 U.S. 181" --corpus-backend ranged`
   - stderr: `ranged corpus reads: 418 GET(s), 109576192 byte(s)`
   - 0 rows returned (no corpus priors citing Burdick/Anderson/Crawford).

## Base rates

- Read the committed `metrics/statpack.md`: modern discretionary-cert
  disposition split, originating-circuit cut (ca3: granted 2.9% of resolved),
  relist cut, **CVSG cut (cvsg: granted 27.1%, denied 71.2%, n=59 resolved)** —
  the primary quantitative anchor — and the per-Term table (2025 Term est.
  grant rate 2.5%).

## CourtListener MCP

- None. The provisioned snapshot (fetched today, 2026-07-16) already carried the
  complete docket through the June 29 CVSG, so no MCP lookups were needed.

## Web searches (engine WebSearch, forward-mode signal)

1. `Baxter v. Philadelphia Board of Elections Pennsylvania Supreme Court decision date requirement mail ballot 2026`
   — Baxter granted review Jan. 17, 2025; argued Sept. 10, 2025; no decision
   found on the public record. (votebeat.org, aclupa.org, statecourtreport.org)
2. `Pennsylvania Supreme Court Baxter undated mail ballots ruling decided`
   — same result; Commonwealth Court (Oct. 30, 2024) had held rejection of
   undated ballots violates the Pa. Constitution; Pa. Supreme Court decision
   still pending. (votebeat.org, democracydocket.com)
3. `Supreme Court cert granted election law 2026 "RNC" OR "Republican National Committee" mail ballots Watson Wetzel`
   — Watson v. RNC, No. 24-1260, decided June 29, 2026 (5–4, Barrett, J.):
   federal election-day statutes do not preempt Mississippi's post-Election Day
   ballot-receipt grace period. Used only as context on the Court's current
   engagement with mail-voting cases; it is a different question and reveals
   nothing about this petition's outcome. (supremecourt.gov, scotusblog.com,
   ballotpedia.org)

None of the retrieved material postdates or reveals this case's disposition
(none exists — the petition awaits the SG's CVSG brief).
