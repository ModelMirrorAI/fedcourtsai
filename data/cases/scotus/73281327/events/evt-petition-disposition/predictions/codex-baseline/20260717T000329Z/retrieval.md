# Retrieval beyond provisioned inputs

## Committed base rates

- Read `metrics/statpack.md`, especially “Modern discretionary-cert petitions by disposition,” originating-circuit, relist, CVSG, and per-Term tables.

## Corpus lookups

Each lookup failed because the ranged corpus remote's host could not be resolved. The commands failed before a corpus read completed, so none emitted a `ranged corpus reads: …` line and none returned priors.

- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
- `uv run fedcourts query --court scotus --era 2020s --citation "Lawrence v. Chater" --limit 10`
- `uv run fedcourts query --court scotus --era 2020s --citation "Video Privacy Protection Act" --limit 10`

## CourtListener MCP

- Searched published Sixth Circuit opinions for `Salazar v. Paramount Global`, limited to January 1, 2025 through July 16, 2026. Found *Michael Salazar v. Paramount Global*, 133 F.4th 642, No. 23-5748, filed April 3, 2025 (`/opinion/10372262/michael-salazar-v-paramount-global/`).
- Searched published Second Circuit opinions for `Salazar v. National Basketball Association`, limited to January 1, 2024 through July 16, 2026. No result was returned.
- Searched published Seventh Circuit opinions for `Gardner v. Me-TV National Limited Partnership`, limited to January 1, 2025 through July 16, 2026. No result was returned.
- Repeated the *Salazar v. Paramount Global* search requesting snippet/download fields to identify available fields; the same single result was returned.
- Repeated the *Salazar v. Paramount Global* search requesting cluster, opinion, and panel metadata. It identified cluster `10372262` and combined-opinion record `10838850`.
- Retrieved CourtListener opinion record `10838850`, fields `id`, `type`, and `html_with_citations`. The opinion confirmed Judges Nalbandian and Batchelder in the majority and Judge Bloomekatz in dissent, and supplied their competing readings of the VPPA.

No web search was used, and no lookup sought this petition's disposition.
