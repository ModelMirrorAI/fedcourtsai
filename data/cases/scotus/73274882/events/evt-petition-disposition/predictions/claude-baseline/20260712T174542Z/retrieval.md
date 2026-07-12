# Retrieval log — scotus/73274882 evt-petition-disposition (claude-baseline, 20260712T174542Z)

Mode: `forward` (pending petition) — retrieval unrestricted per the contract.

## Committed base rates

- Read `metrics/statpack.md` — "Modern discretionary-cert petitions by
  disposition" (grant ~4.9%, denied ~92.6%), "Modern cert petitions by
  originating circuit" (ca9: 94.7% denied / 5.3% granted), and the per-Term
  table (Term 2025, paid filings). The relist-count and CVSG cuts were
  `(unknown)` for the whole population, so the relist signal was reasoned
  qualitatively.

## Corpus lookups (`fedcourts` CLI, ranged reads)

1. `uv run fedcourts query --court scotus --citation "597 U.S. 1" --citation "554 U.S. 570" --era 2020s`
   — no rows returned.
   stderr: `ranged corpus reads: 402 GET(s), 105381888 byte(s)`
2. `uv run fedcourts query --court scotus --era 2020s`
   — returned ~11 ranked 2020s SCOTUS priors. Key yield: Viramontes v. Cook
   County (25-238, ca7, distribution_count 22) and Grant v. Higgins (25-566,
   ca2, distribution_count 17) both show `date_cert_granted: 2026-06-30`;
   McCoy v. ATF (25-24) and WVCDL v. ATF (25-132) show
   `date_cert_denied: 2026-06-30` — i.e., grants and denials issued from the
   same 6/29/2026 conference at which Duncan was last distributed with no
   action.
   stderr: `ranged corpus reads: 402 GET(s), 105381888 byte(s)`

(An initial `fedcourts query` invocation used an unsupported `--docket` flag
and errored without reading the corpus; `--help` was consulted.)

## Web searches (engine WebSearch; 2 calls)

1. Query: `Duncan v. Bonta supplemental brief "Benson" Supreme Court magazine
   ban 2026` — purpose: identify the "Benson" decision behind the March/April
   2026 supplemental briefs on this docket. Yield: Benson is a D.C. Court of
   Appeals decision (early March 2026) holding D.C.'s 10+ round magazine ban
   violates the Second Amendment, expressly splitting with the Ninth Circuit's
   Duncan decision and the D.C. Circuit's Hanson; Duncan had ~19 relists as of
   June 1, 2026. Sources consulted: supremecourt.gov docket PDFs (25-198 /
   25-421 supplemental briefs), calgunlawyers.com relist commentary.
2. Query: `Viramontes v. Cook County cert granted June 30 2026 question
   presented assault weapons magazines Grant v. Higgins` — purpose: scope of
   the June 30, 2026 grants and the fate of the magazine-ban petitions.
   Yield: cert granted and consolidated in Viramontes (25-238) and Grant v.
   Higgins (25-566), limited to whether the Second/Fourteenth Amendments
   protect AR-15-platform and similar semiautomatic rifles in common use;
   argument expected early OT2026; the magazine cases — Duncan (25-198),
   Gator's Custom Guns v. Washington (25-153), NAGR v. Lamont (25-421) — were
   held over to next term rather than denied. Sources consulted: SCOTUSblog
   case page, SAF press release, JURIST news item, secondary 2A-community
   reporting.

## CourtListener MCP

- Server was configured and its `search` tool schema was loaded, but no MCP
  calls were ultimately needed: the provisioned snapshot (docket current to
  2026-07-10), corpus query results, and the two web searches answered every
  open question. No REST fallback used; no MCP errors observed.

Nothing retrieved concerned this case's own (nonexistent) disposition; the
searches concerned related cases' cert grants and an intervening lower-court
decision, all permissible in forward mode.
