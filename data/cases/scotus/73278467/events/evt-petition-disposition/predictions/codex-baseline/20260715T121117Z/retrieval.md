# Retrieval

## Committed base rates

- Consulted `metrics/statpack.md` and `metrics/statpack.json` for modern discretionary-cert, originating-circuit, relist, CVSG, Term, and paid/IFP base rates.

## Corpus lookup

- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --era 2020s --citation 'United States v. Skrmetti, 145 S. Ct. 1816 (2025)' --limit 10 --corpus-backend ranged` — sought comparable recent SCOTUS priors citing *Skrmetti*. The lookup failed before any result or ranged-read statistic because DNS resolution for the corpus-store host failed; there was no `ranged corpus reads: ...` line.

## CourtListener MCP

- Searched SCOTUS opinions filed from November 1, 2025 through July 15, 2026 for *West Virginia v. B. P. J.* or *Little v. Hecox* to identify intervening controlling authority.
- Repeated the exact *West Virginia v. B. P. J.* search with restricted metadata fields to identify the opinion cluster.
- Retrieved the cluster's opinion metadata and opinion-record identifier.
- Retrieved CourtListener opinion record 11349709, using its text to review the syllabus, holding, vote alignment, and treatment of intermediate scrutiny and transgender-status classifications.
- Searched Tenth Circuit opinions filed from August 1, 2025 through July 15, 2026 for a post-remand *Fowler v. Stitt* decision; the search returned no results.

No web searches were used.
