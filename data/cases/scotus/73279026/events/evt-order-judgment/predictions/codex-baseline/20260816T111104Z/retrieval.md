# Retrieval

- Read the committed `metrics/statpack.md` merits section and its per-grant-Term table. No corpus query was run, so there is no ranged-corpus-read line.
- Retrieved the petitioners' June 2026 merits brief from the official Supreme Court PDF URL recorded in the provisioned snapshot: `https://www.supremecourt.gov/DocketPDF/25/25-581/415025/20260625143739952_St%20Mary%20Opening%20Br%20FINAL.pdf`.
- Retrieved the United States' July 2026 merits amicus brief from the official Supreme Court PDF URL recorded in the provisioned snapshot: `https://www.supremecourt.gov/DocketPDF/25/25-581/415681/20260702225636069_25-581tsacUnitedStates.pdf`.
- CourtListener MCP opinion search: `("general applicability" OR "generally applicable") AND (Carson OR Fulton) AND "religious exercise"`, Supreme Court opinions filed from 2020-01-01 through 2026-08-16. The results identified Fulton, Carson, Kennedy, and Mahmoud.
- CourtListener MCP `read_document` lookup for opinion id 10618551. The identifier resolved to an unrelated South Carolina opinion because the first search result exposed a cluster-style URL rather than the underlying opinion id; I discarded it and used none of its content.
- CourtListener MCP exact case-name search for `Mahmoud v. Taylor`, Supreme Court opinions filed from 2025-06-01 through 2025-07-15. This returned the combined-opinion record and underlying opinion id 11085139.
- CourtListener MCP `read_document` lookup for opinion id 11085139, first 12,000-character chunk, to check Mahmoud's holding.
- CourtListener MCP `search_document` lookup for `ROBERTS` within opinion id 11085139 to confirm the six-Justice majority and three-Justice dissent.
