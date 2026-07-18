# Retrieval log — scotus/73500221 · evt-petition-disposition · claude-baseline · 20260718T064904Z

## Corpus lookups (fedcourts CLI)

1. `uv run fedcourts query --court scotus --era 2020s --citation "588 U.S. 180" --limit 5`
   — stderr: `corpus service at http://127.0.0.1:8377 is unreachable — is the sidecar running? (fedcourts corpus-serve): timed out`
   (no `ranged corpus reads:` line; no rows returned)
2. Same command retried once — same timeout. No further corpus-query attempts;
   fell back to the committed statpack per the degraded-upstream rule.

## Base rates

- `metrics/statpack.md` — "Modern discretionary-cert petitions by disposition",
  "Modern cert petitions by originating circuit" (ca10), "Cert petitions by
  relist count" (bucket 0), "Cert petitions by CVSG status" (none), and the
  per-Term table (Term 2025).
- `metrics/statpack.json` — per-Term fee-class detail (Term 2025 paid grant
  rate ≈ 5.4%, IFP ≈ 1.1%). The salience-band table named in the prompt is
  not present in this statpack build.

## CourtListener MCP lookups

1. `search` (type=o, q="Rogne v. City of Catoosa", court=ca10) — 0 results
   (the Tenth Circuit order and judgment is not in the opinion index).
2. `search` (type=o, q="Rogne Catoosa") — 0 results.
3. `search` (type=d, q="Rogne Catoosa") — found the Tenth Circuit docket
   (No. 25-5039, docket id 72285743) and the N.D. Okla. docket
   (4:24-cv-00307, filed 2024-06-28), confirming the procedural history in
   the petition. No information about this case's SCOTUS disposition was
   sought or surfaced (the petition is pending; first conference 2026-09-28).

## Web searches

None.
