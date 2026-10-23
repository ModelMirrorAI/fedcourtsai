# Retrieval log

- Consulted the committed `metrics/statpack.md`, especially “The merits docket (granted cases),” and inspected the top-level keys of `metrics/statpack.json` for metadata. Computed the strictly-prior grant-Term pool from the markdown rows with a local Python command: 360 disturbed / 516 parsed, 539 granted, Terms 2017–2024 within the allowed 2015–2024 window. No live corpus lookup was made, so no ranged-corpus transfer line was emitted.
- Web search attempted for general precedent only: `site.supremecourt.gov opinions 2018 Kisor Wilkie 18-15 pdf` and `site.supremecourt.gov opinions 2023 Loper Bright 22-451 pdf`. The tool returned no usable results or source text.
- Web open attempted for the Supreme Court's Kisor opinion PDF, path `/opinions/18pdf/18-15_9p6b.pdf` on `www.supremecourt.gov`. The tool returned no usable text. No information from that attempted retrieval informed the forecast.
- CourtListener MCP `search`: `type="o"`, `citation="588 U.S. 558"`, `num_results=1`, `fields=["caseName","dateFiled","citation","opinions"]`. Returned HTTP 429 with a rate-limit message; no case text or results received. Degraded to the provisioned filings and committed pack; no REST fallback attempted.
- No searches for Beaird's disposition, later docket history, merits briefing, or decision coverage; no other predictions or outcome artifacts consulted.
