# Retrieval Log — scotus/73266074, evt-petition-disposition

The following retrieval sources were consulted during the prediction process:

1. **Provisioned Case Files:**
   - Case Snapshot: `data/cases/scotus/73266074/record/snapshots/2026-07-10.json` (analyzed proceedings, dates, CFR signal, and extension motion).
   - Document Text: `data/cases/scotus/73266074/record/documents/questions-presented.txt` (read the Contract Clause and Bill of Attainder legal questions).
   - Case Metadata/Context: `data/cases/scotus/73266074/record/context.json` and `data/cases/scotus/73266074/record/documents/documents.json`.

2. **Google Web Search:**
   - Performed targeted searches to understand the background of the *Hastings College Conservation Committee v. California* dispute, the California Court of Appeal First Appellate District decision, the arguments of the parties, and potential circuit splits or tensions (e.g., with *Trustees of Dartmouth College v. Woodward* and the D.C. Circuit's *Foretich v. United States*).
   - Crucially, searches were crafted to avoid retrieving the final outcome of the Supreme Court petition (Case No. 25-1231 / 25-1334) to remain completely insulated under the timing leak avoidance doctrine.

3. **Ecosystem & CLI Tools:**
   - Consulted the committed `metrics/statpack.md` as a baseline reference for overall SCOTUS and circuit-specific base rates.
   - Attempted to run the `fedcourts query` CLI command, but the local corpus database was not pulled and the environment lacked the DVC remote URL required for remote ranged reads.

4. **CourtListener MCP Server:**
   - Not utilized for case-specific dockets to prevent any risk of outcome exposure under the leak doctrine, and because the general web search and provisioned documents provided complete factual context for the pending stage.
