# Retrieval log — claude-baseline, run 20260917T181231Z

Forward-mode cell; the conference (2026-09-28) postdates the snapshot, so no leakage clock applies. Eight calls total, well inside the advisory budget.

## Corpus tooling

- `uv run fedcourts query --court scotus --era 2020s --limit 8` (corpus service backend from the cell environment). Returned eight recent SCOTUS rows, all stay/extension applications or a dismissed IFP petition, none a mandamus-alike prior. stderr: `ranged corpus reads: 6 GET(s), 1572864 byte(s)`.
- `metrics/statpack.md` (committed): Modern discretionary-cert petitions by disposition; Cert petitions by relist count / CVSG status / salience band (paid scored segment); SCOTUS cert petitions by Term; Segment base rate by salience band (sal-v4), pooled over OT2017–OT2024 for the baseline band.
- `fedcourtsai.pipeline.moments.spec_for` / `claims.declared_claim_set` for `evt-petition-disposition` (confirms stage cert, moment distribution, claim set cert-v2).

## CourtListener MCP

- `search` type=d, party_name="Joan Farr" — **HTTP 429** (rate limit 300/hour exceeded; ~878 s to reset). No results.
- `search` type=o, q="Joan Farr" grantLove OR "Alexandra Grant" OR "WME" — **HTTP 429**. No results.
- No further MCP calls; degraded to web search per the prompt's fallback.

## Web

- WebSearch: `"Joan Farr" "grantLove" OR "Alexandra Grant" lawsuit Missouri Kansas court` — surfaced *Farr v. Grant et al.*, W.D. Mo. No. 4:24-cv-00439 (filed 2024-07-01, pro se), and Eighth Circuit No. 25-1525 (judgment 2025-10-10).
- WebSearch: `"Farr v. Grant" 8th Circuit 25-1525 Joan Farr pro se affirmed dismissal ...` — same sources plus a 2022 D. Kan. suit by the same petitioner against the United States Government (No. 2:22-cv-02476); no opinion text.
- WebFetch https://law.justia.com/cases/federal/appellate-courts/ca8/25-1525/25-1525-2025-10-10.html — HTTP 403.
- WebFetch https://www.courtlistener.com/docket/68910257/farr-v-grant/ — HTTP 403.
- WebFetch https://www.govinfo.gov/app/details/USCOURTS-ca8-25-01525/context — page loaded without content.

Nothing retrieved concerned this petition's own disposition, which does not yet exist.
