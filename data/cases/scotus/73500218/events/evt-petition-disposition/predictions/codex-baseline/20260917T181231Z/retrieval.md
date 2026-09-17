# Retrieval log

## Local inputs and base rates

- Read AGENTS.md, .github/prompts/predict.md, and the prediction, agent-flags, and agent-tooling schemas.
- Read this cell's event.yaml, record/context.json, and record/snapshots/2026-09-17.json. No record/documents directory was present.
- Consulted metrics/statpack.md, specifically modern-cert dispositions, the paid-segment relist/CVSG cuts, and the sal-v4 per-Term reached-band table. Read statpack.json for unrounded baseline prefix rates and denominators; pooled displayed Terms 2017–2024 with an in-memory Python calculation. Used git log to identify the pack's last modifying commit and date.
- Ran `uv run fedcourts paths --court scotus --docket 73500218 --event evt-petition-disposition --role predictor`. The first attempt failed on the read-only default uv cache; reran successfully with a temporary cache directory. No corpus query or open-events command was run, and no ranged-corpus-transfer line was emitted.
- No CourtListener MCP lookup was made.

## External retrieval, September 17, 2026

The web tool returned no usable content for these attempts:

1. Opened the exact pre-decision petition PDF identified in the snapshot [R2].
2. Searched `site.supremecourt.gov "Rule 20" "exceptional circumstances"` for the generic extraordinary-writ rule, not the case.
3. Opened the official rules-and-guidance page twice [R0].
4. Attempted a find for `Issuance by the Court` in the official 2026 rules PDF [R1], then opened that PDF.

Direct official-source reads then succeeded without any CourtListener fallback or credentials:

- R0: `https://www.supremecourt.gov/filingandrules/rules_guidance.aspx` — fetched with curl, extracting PDF links only; this confirmed the linked 2026 rules filename.
- R1: `https://www.supremecourt.gov/filingandrules/2026RulesoftheCourt_WEB.pdf` — fetched into memory with httpx and read with pypdf. The PDF has 86 pages; the text search returned PDF pages 28–29, printed pages 24–25, containing Rule 20. Read the extraordinary-writ standard and mandamus response procedure. This supplied general legal context only.
- R2: `https://www.supremecourt.gov/DocketPDF/25/25-1315/410989/20260527154626098_scan_ajimenez_2026-05-27-15-42-32.pdf` — exact petition link from the May 20, 2026 filing entry; fetched into memory with httpx and checked with pypdf. All 22 pages returned zero extracted characters. No substantive petition text was obtained; no OCR or visual reading occurred.

No current case-docket page, subsequent history, case-disposition search, or outcome file was consulted. No outcome was encountered. Retrieved PDFs were not copied into the output directory or the provisioned record.
