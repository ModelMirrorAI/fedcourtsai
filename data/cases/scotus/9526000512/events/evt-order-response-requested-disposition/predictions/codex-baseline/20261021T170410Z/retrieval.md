# Retrieval beyond provisioned inputs

## Committed base-rate material

Read metrics/statpack.md, specifically **The interim docket (applications)** and its per-Term table. Used only the 2016–2025 window for a Term 2026 application: 51 grants / 547 resolved substantive applications. This is the committed pack, not a fresh corpus pull. No fedcourts query or open-events lookup was made, so there is no ranged-corpus transfer line to report.

## Web attempts

The web tool returned no usable source content for these general-doctrine requests:

1. Search: `site.supremecourt.gov opinions 2006 Purcell Gonzalez 549 1 pdf`.
2. Search: `site.supremecourt.gov opinions Merrill Milligan 2022 Kavanaugh Purcell entirely clearcut`.
3. Open attempt: the GovInfo U.S. Reports PDF for **549 U.S. 1**, path `content/pkg/USREPORTS-549/pdf/USREPORTS-549-1.pdf`.

No factual support was taken from those empty responses. None sought this application's docket, disposition, or subsequent history.

## CourtListener MCP

1. `search(type="o", citation="549 U.S. 1", num_results=1)`: returned an unrelated **United States v. Acosta-Roman**, 549 F.3d 1 (2008), opinion 203572. Disregarded; no opinion text read and no inference drawn.
2. `search(type="o", case_name="Purcell v. Gonzalez", court="scotus", num_results=1)`: located the October 20, 2006 decision, 549 U.S. 1, cluster 145774.
3. `read_document(opinion_id=9435151)`: read the Purcell lead opinion, particularly pages 4–6, for its election-proximity, voter-confusion, and interim-versus-final-merits reasoning. This is general precedent, not this application's outcome.

No direct CourtListener REST requests were made. No lookup sought the present application's own disposition, post-baseline proceedings, or decision coverage. The recent authorities attributed to docket 26A274 in the supplied application were not retrieved or treated as verified precedent.
