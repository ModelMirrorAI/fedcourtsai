# Retrieval account

## Provisioned inputs

Read the event definition and case-level record: `context.json`, `snapshots/2026-10-25.json`, `documents/documents.json`, `documents/questions-presented.txt`, and relevant parts of `documents/petition.txt`, including the appended Third Circuit decision. No other prediction, evaluation, realized outcome, or QP-labeling artifact was read.

## Committed base-rate context

Read `metrics/statpack.md`: matching sal-v4 risk-set band table, paid-scored-segment relist and CVSG cuts, and the general cert table headings. Used the displayed baseline-band reached rates for Terms 2017–2024, excluding this case's Term 2025 and later rows. An in-memory Python calculation pooled the rounded table percentages over the printed denominators: 0.0512025043, denominator 11,580. No `fedcourts query`, `open-events`, or other live corpus lookup was made, so there are no ranged-corpus transfer lines to report.

## General legal context only

Web searches:

1. `site.supremecourt.gov opinions Sprint Communications Jacobs 571 69 2013 Younger`
2. `site.ca4.uscourts.gov Harper Public Service Commission 396 F.3d 348 Younger`

Read the primary opinion in **Sprint Communications, Inc. v. Jacobs**, 571 U.S. 69 (2013), from the official United States Reports PDF, focusing on the limited Younger categories and the distinction between those categories and the additional Middlesex factors. The official source was opened twice:

`https://www.govinfo.gov/content/pkg/USREPORTS-571/pdf/USREPORTS-571-69.pdf`

The Fourth Circuit's official opinion in **Air Evac EMS, Inc. v. McVey**, No. 21-1301 (June 10, 2022), was located while checking the petition's characterization of Harper. Searched within that PDF for `Harper` twice and opened the opinion, focusing on its discussion of NOPSI and Harper on PDF pages 10–12. This qualified my assessment of the asserted circuit split; it supplied no information about the target petition.

`https://www.ca4.uscourts.gov/opinions/211301.P.pdf`

No CourtListener MCP lookup was needed. No search used this case's caption, docket number, disposition, or subsequent history. No target outcome or outcome-revealing material was encountered.

## Operational checks

Read the governing prompt and schemas and the repository path, identifier, and serialization helpers. `uv run fedcourts paths --court scotus --docket 73500260 --event evt-petition-disposition --role predictor` initially failed because the default uv cache location was read-only; the same command succeeded with `uv --no-cache run`. Validation uses the same no-cache setting. These operational reads added no case evidence.
