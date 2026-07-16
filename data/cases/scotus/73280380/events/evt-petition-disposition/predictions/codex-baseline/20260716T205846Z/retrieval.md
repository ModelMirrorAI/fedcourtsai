# Retrieval

## Committed base rates

- Consulted `metrics/statpack.md`, including modern discretionary-cert disposition, originating-circuit, relist, CVSG, and per-Term tables.
- Consulted `metrics/statpack.json` for the 2025 Term paid-petition estimate: 5.36% granted.

## Corpus lookup

- `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --topic 'Rule 11 sanctions' --era 2020s --limit 5`
  - The lookup failed before returning results because the runner could not resolve the remote corpus-store endpoint. It emitted no `ranged corpus reads: ...` line.

## CourtListener MCP

- `search`: Supreme Court opinions for `"Rule 11" sanctions`, filed before 2026-07-16. The results included *Cooter & Gell v. Hartmarx Corp.*, 496 U.S. 384 (1990), among less relevant matches.
- `search`: exact case-name search for *Bost v. Illinois State Board of Elections*. This formulation returned no results.
- `search`: Supreme Court opinions for `Bost Illinois State Board Elections candidate standing`, filed before 2026-07-16. This located *Bost v. Illinois Bd. of Elections*, No. 24-568, decided January 14, 2026.
- `get_endpoint_item` (`clusters`, 10774336): confirmed the *Bost* case metadata and linked opinion.
- `get_endpoint_item` (`opinions`, 11240921): consulted the *Bost* opinion and syllabus. The holding recognizes a candidate's concrete interest in the rules governing vote counting regardless of effect on electoral prospects; it does not decide sanctions standards.

No web searches were used. No lookup sought this case's disposition or subsequent history.
