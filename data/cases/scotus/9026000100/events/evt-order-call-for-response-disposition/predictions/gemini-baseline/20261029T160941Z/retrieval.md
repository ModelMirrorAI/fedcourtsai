# Retrieval Log (`scotus/9026000100` — `evt-order-call-for-response-disposition`)

## 1. Provisioned Case Record & Committed Base-Rate Artifacts
- `data/cases/scotus/9026000100/events/evt-order-call-for-response-disposition/event.yaml`
- `data/cases/scotus/9026000100/record/context.json` (`mode: "forward"`, `cutoff: "2026-08-14"`, `band: "baseline"`, `salience_version: "sal-v4"`)
- `data/cases/scotus/9026000100/record/snapshots/2026-08-13.json`
- `data/cases/scotus/9026000100/record/documents/documents.json`
- `data/cases/scotus/9026000100/record/documents/questions-presented.txt`
- `data/cases/scotus/9026000100/record/documents/petition.txt` (including Appendix A: Ninth Circuit memorandum disposition, Jan. 13, 2026; Appendix B: Northern District of California summary judgment order, Sept. 3, 2024; Appendix C: order denying rehearing en banc, Feb. 20, 2026; Appendix D: Declaration of Shannon Cross; Appendix E: Declaration of David Brinton)
- `metrics/statpack.md` (SCOTUS discretionary-cert base rates by salience band `sal-v4`, originating circuit `ca9`, relist count, CVSG status, and cert amicus count)

## 2. Corpus Queries (`uv run fedcourts query`)

1. **Recent 2020s SCOTUS granted priors:**
   - Command: `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 5`
   - Transfer: `ranged corpus reads: 27 GET(s), 7077888 byte(s)`
   - Purpose: Inspect recent SCOTUS cert grant rows and metadata structure (including distribution counts, salience scores, and originating circuits).

2. **Recent 2020s SCOTUS denied priors:**
   - Command: `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 5`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Purpose: Inspect recent SCOTUS denial rows from the warm cache.

3. **Citation lookup test for *Ames* (`605 U.S. 303`) and *Hittle* (`145 S. Ct. 759`):**
   - Command: `uv run fedcourts query --court scotus --citation "605 U.S. 303" --citation "145 S. Ct. 759" --limit 5`
   - Transfer: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
   - Result: 0 rows (parallel citations column sparsely populated on recent SCOTUS rows; followed up via `--docket-number`).

4. **Docket lookup for *Ronald Hittle v. City of Stockton, California, et al.* (`24-427`):**
   - Command: `uv run fedcourts query --court scotus --docket-number 24-427`
   - Transfer: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - Result: Retrieved `scotus/69719675` (*Ronald Hittle v. City of Stockton, California, et al.*, No. 24-427, originating from `ca9` No. 22-15485, filed 2024-10-16, `distribution_count: 5`, `salience_score: 0.4108`, 10 amicus counsel appearances, `disposition: "denied"` on 2025-03-10). Directly informs the comparison between *Hittle* and Cross's petition.

5. **Docket lookup for *Marlean A. Ames v. Ohio Department of Youth Services* (`23-1039`):**
   - Command: `uv run fedcourts query --court scotus --docket-number 23-1039`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Retrieved `scotus/69676206` (*Marlean A. Ames v. Ohio Department of Youth Services*, No. 23-1039, originating from `ca6`, `distribution_count: 3`, `salience_score: 0.4095`, `disposition: "granted"` on 2024-10-04, `merits_judgment: "vacated"` on 2025-06-05).

6. **Panel judge overlap query (`Jacqueline H. Nguyen`, `Mark J. Bennett`):**
   - Command: `uv run fedcourts query --court scotus --judge "Jacqueline H. Nguyen" --judge "Mark J. Bennett" --limit 10`
   - Transfer: `ranged corpus reads: 640 GET(s), 167575552 byte(s)`
   - Result: 0 SCOTUS rows with `judges` populated for the Ninth Circuit panel members.

## 3. CourtListener MCP Lookups
- Attempted two opinion searches via `mcp_courtlistener_search` for `Hittle v. City of Stockton` and `Ames v. Ohio Department of Youth Services` (`court="scotus"`, `type="o"`). Both calls returned `HTTP 429: Rate limit exceeded: 1400/day`. Because the full text of the lower-court opinions in Cross's case is bound into `record/documents/petition.txt` (Appendices A–C) and the SCOTUS docket records for *Hittle* (`24-427`) and *Ames* (`23-1039`) were retrieved directly from the local corpus via `fedcourts query --docket-number`, the CourtListener rate limit did not impair the analysis.
