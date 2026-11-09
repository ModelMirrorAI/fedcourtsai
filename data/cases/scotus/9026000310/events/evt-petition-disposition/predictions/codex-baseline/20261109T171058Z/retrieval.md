# Retrieval record

## Provisioned and repository material

Read the event definition, November 9, 2026 snapshot, context.json, documents.json, questions-presented.txt, petition.txt, decision-below.txt, lower-court-docket.txt, selected appendix passages, and same-question.json. The appendix is truncated; the independently staged appellate decision is complete. No related-docket files were provisioned. Read the prediction, flags, and tooling schemas and the relevant cert portions of the prediction contract. Consulted metrics/statpack.md and metrics/statpack.json for grant priors and signal cuts, including a direct aggregation of the prior-Term baseline reached-band anchor. These are local repository reads, not corpus queries. No predictions or evaluations belonging to another cell were read.

## External calls

1. One web search call contained two queries:
   - `site.supremecourt.gov opinions 2024 Ames Ohio Department Youth Services 23-1039 2025`
   - `site.eeoc.gov What You Should Know DEI Related Discrimination Work training hostile work environment question 10`
   The search returned the official Supreme Court Ames syllabus/opinion, No. 23-1039, June 5, 2025, and the official EEOC question-and-answer guidance dated March 19, 2025. The EEOC result supplied question 10's discussion of training and hostile environments. Search results also surfaced third-party discussions, an EEOC press-release result and Spanish guidance, and an unrelated case-analytics result for Ames. Those incidental results were not opened or used. No result disclosed the disposition of Young's petition.
2. Opened the official Supreme Court Ames opinion PDF identified in the first search, document filename `23-1039_c0n2.pdf`. The tool returned a 17-page PDF, with the syllabus and opening opinion discussing the rejection of the majority-group background-circumstances requirement. Used this only for general legal context and to distinguish Ames from an intervening severity decision. The official PDF contains an internal June 4/June 5 discrepancy on its opening syllabus page; the opinion cover and official search metadata identify the decision as June 5, 2025. Nothing in the forecast depends on that one-day difference.

No CourtListener MCP calls, fedcourts corpus queries, open-events lookups, live searches for Young, or retrievals of this petition's disposition or later history were attempted. There were no failed or refused external calls. The required local cell-validation command is a schema/completeness check, not a retrieval of case outcomes.

## Local validation

- Attempted `uv run fedcourts validate data --cell data/cases/scotus/9026000310/events/evt-petition-disposition/predictions/codex-baseline/20261109T171058Z`; uv stopped before validation because its default cache directory was read-only.
- Retried with `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts validate data --cell data/cases/scotus/9026000310/events/evt-petition-disposition/predictions/codex-baseline/20261109T171058Z`; the validator printed `OK: 30120 artifact(s) valid, 71659 reference(s) consistent; cell complete`. The cache override and no-sync option avoid changing the provisioned environment or installing packages. Repeated the same successful command after recording this note.
