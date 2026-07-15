# Retrieval log — scotus/73278426 · evt-petition-disposition · claude-baseline · 20260715T072005Z

Mode: `forward` (retrieval unrestricted; no outcome exists for this petition).

## Corpus / committed base rates

- Read committed `metrics/statpack.md` — modern discretionary-cert base rates
  (grant ≈ 2.5–3%/Term), relist-count cut (3+ relists → granted 21.8%), CVSG
  cut, per-circuit cuts. No salience-band table present in this statpack.
- `uv run fedcourts query --court scotus --era 2020s --citation "597 U.S. 1" --limit 8`
  → no matching priors. stderr: `ranged corpus reads: 415 GET(s), 108789760 byte(s)`
- `uv run fedcourts query --court scotus --era 2020s --citation "554 U.S. 570" --citation "142 S. Ct. 2111" --limit 8`
  → no matching priors. stderr: `ranged corpus reads: 415 GET(s), 108789760 byte(s)`

## Web (engine WebSearch/WebFetch)

- WebSearch: `Supreme Court cert granted assault weapons ban 2026 Duncan v. Bonta OR "Gator's Custom Guns" OR Benson`
  — purpose: identify the companion-case landscape and the "Benson" letter
  referenced on the docket. Key results: JURIST (7/2026 cert grants in
  Viramontes v. Cook County and Grant v. Higgins, consolidated), ammoland.com
  strategy piece, calgunlawyers.com on Duncan relists, Duke Firearms Law gun
  watch, thetrace.org.
- WebFetch: https://www.jurist.org/news/2026/07/us-supreme-court-agrees-to-hear-challenges-to-assault-weapons-bans/
  — purpose: confirm grant date and cases. Confirmed: cert granted July 2,
  2026 in Viramontes v. Cook County (CA7) and Grant v. Higgins (CA2),
  consolidated for fall 2026 argument.
- WebFetch: https://www.ammoland.com/2026/07/supreme-court-delay-ar-15-case-2a-strategy/
  — purpose: what else happened on that order list. Confirmed: Duncan v.
  Bonta (25-198) and Washington v. Gator's Custom Guns (25-153) were held,
  not granted; docket numbers Viramontes 25-238, Grant 25-566.
- WebSearch: `"NAGR" OR "National Association for Gun Rights" "25-421" Lamont Supreme Court held July 2026`
  — purpose: current status of this petition after the July 2 order list.
  No July 2026 order reported; latest activity remains the 6/29/2026
  distribution.
- WebFetch: https://www.supremecourt.gov/docket/docketfiles/html/public/25-421.html
  — purpose: verify current docket state. **Failed (HTTP 403)**; not retried.
- WebFetch: https://www.scotusblog.com/cases/national-association-for-gun-rights-v-lamont/
  — purpose: same verification via SCOTUSblog case page. Confirmed petition
  still pending; most recent entry the 6/29/2026 distribution; no grant,
  denial, or hold order shown.

## CourtListener MCP

Not used — the provisioned snapshot, committed statpack, and the web lookups
above answered everything needed; no MCP call was made (so no REST fallback
either).
