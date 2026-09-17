# Retrieval log

Mode: `forward` (retrieval unrestricted). Conference is 9/28/2026; nothing retrieved disclosed a disposition.

## Corpus (`fedcourts query`, ranged backend)

1. `uv run fedcourts query --court scotus --citation "542 U.S. 155" --limit 5`
   - `ranged corpus reads: 1357 GET(s), 355663872 byte(s)`
   - `note: citations filter: 200 of 590940 rows in scope (scotus) carry citation data ...` — empty result (coverage gap, not "no such case").
2. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 12`
   - `ranged corpus reads: 11 GET(s), 2883584 byte(s)`
   - 12 recent granted rows, used for shape only (recent grants cluster at 2–5+ distributions; one carried a CVSG). No subject match possible — the CLI has no free-text filter on SCOTUS rows.

## CourtListener MCP

3. `search` type=o, court=ca9, q=`"NHK Spring" Seagate FTAIA` → cluster 10771069, *Seagate Technology LLC v. NHK Spring Co.*, No. 24-4470, filed 2026-01-08, Published.
4. `search` type=d, court=scotus, docket_number=25-1358 → 0 results (the SCOTUS docket is not in RECAP).
5. `read_document` opinion_id=11237654, chunk 0 of 12 → panel (Callahan, Lee, Rash D.J. by designation), opinion by Judge Lee, staff summary, counsel list (three amici below: Prof. Elzinga, American Antitrust Institute, Prof. Ryngaert).

## Web searches (engine-surfaced)

6. `"NHK Spring" Seagate Supreme Court certiorari FTAIA petition 25-1358` → supremecourt.gov BIO PDFs, Kluwer Competition Law Blog commentary, AAI amicus note (Ninth Circuit stage).
7. `Seagate v. NHK Spring Ninth Circuit FTAIA Motorola circuit split January 2026` → ASIL, Concurrences, Mondaq, Justia summaries of the Ninth Circuit decision.
8. `"NHK Spring" Seagate cert petition Supreme Court "September 28" OR "long conference" OR "petitions to watch" 2026` → Law360 headline "Seagate Urges Justices Not To Review NHK Antitrust Case"; no petitions-to-watch listing found.
