# Retrieval record

## Committed general context

- Read `metrics/statpack.md`: modern discretionary-cert dispositions,
  originating-circuit cut, paid-scored relist and CVSG cuts, and the sal-v4
  per-Term segment table.
- Read `metrics/statpack.json` for exact baseline reached denominators and
  rates. A local Python calculation pooled Terms 2017–2025 only:
  659 / 12,912 = 0.05103779429987609. No live corpus was queried, and no
  corpus-transfer line was produced. The paid amicus-count cut is absent.
- Used the repository path resolver and read artifact schemas and path /
  serialization helpers for output compliance; these were not case evidence.

## CourtListener MCP

1. `search(type="o", citation="918 F.3d 1213", num_results=2,
   fields=["caseName", "dateFiled", "citation", "absolute_url", "opinions"])`.
   Returned *Jacqueline Lewis v. City of Union City, Georgia*, decided
   March 21, 2019; opinion ID 4379419, cluster path
   `/opinion/4602166/jacqueline-lewis-v-city-of-union-city-georgia/`.
2. `search_document(opinion_id=4379419, query="identical", snippet_size=250)`.
   Read excerpts including the majority's rejection of a near-identity
   comparator test and adoption of material similarity. Used only for
   general precedent predating this petition.

No MCP lookup sought this petition, its disposition, or its subsequent history.

## Web attempts

- Search: `site.supremecourt.gov Rule 10 writ of certiorari misapplication
  properly stated rule of law`.
- Open attempt: the Supreme Court's `2023RulesoftheCourt.pdf` under
  `/filingandrules/`.
- Two open attempts: the Supreme Court's `/filingandrules/rules_guidance.aspx`.

These calls returned no readable content to the agent. No web result supplied
facts, authorities, or outcome information used in this forecast.
