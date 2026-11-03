# Retrieval Log (`retrieval.md`)

## 1. Corpus Tooling (`fedcourts`)

1. **Path resolution and CLI help:**
   - Command: `uv run fedcourts paths --court "scotus" --docket "9526000619" --event "evt-motion-disposition" --role predictor && uv run fedcourts query --help`
   - Result: Resolved `case_id` `scotus/9526000619`, corpus `corpus/corpus.db`, and event path; displayed structured filter options for `fedcourts query`.
2. **Recent SCOTUS 2020s resolved priors (substantive applications and petitions):**
   - Command: `uv run fedcourts query --court scotus --era 2020s --limit 10`
   - Transfer line: `ranged corpus reads: 8 GET(s), 2097152 byte(s)`
   - Result: Returned 10 recent OT2026 resolved rows, including substantive stay applications `scotus/9526000602` (*Nichloson v. U.S. Bank National Association*, 26A602, pro se foreclosure application, denied), `scotus/9526000606` (*Silva v. Blanche*, 26A606, denied), `scotus/9526000613` (*Walker v. Purdue Pharmaceuticals*, 26A613, pro se state-court stay, denied), `scotus/9526000617` (*Lancranjan v. Truitt*, 26A617, pro se, denied), `scotus/9526000618` (*Cooper v. Judge Anne Swern*, 26A618, pro se, denied), `scotus/9526000499` (*Louisiana v. Devon Energy Production Co.*, 26A499, denied after response requested), `scotus/9526000535` (*Griffin v. Isaac*, 26A535, pro se state-court stay, denied), and `scotus/9526000532` (*Monte v. United States*, 26A532, denied).
3. **Attempted query with invalid flag `--application-kind`:**
   - Command: `uv run fedcourts query --court scotus --application-kind substantive --era 2020s --limit 10`
   - Result: Failed with exit code 2 (`No such option: --application-kind`).
4. **Recent SCOTUS 2020s granted applications (`--include-applications`):**
   - Command: `uv run fedcourts query --court scotus --include-applications --disposition granted --era 2020s --limit 10`
   - Transfer line: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned 10 granted extension-of-time applications (`26A614`, `26A567`, `26A610`, `26A611`, `26A615`, `26A616`, `26A591`, `26A598`, `26A599`, `26A600`), all marked `application_kind: "extension"` and `predict_excluded: true`.
5. **Recent SCOTUS 2020s granted substantive cases/applications (without `--include-applications`):**
   - Command: `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 10`
   - Transfer line: `ranged corpus reads: 30 GET(s), 7864320 byte(s)`
   - Result: Returned 10 granted rows, including substantive stay/injunction applications `scotus/9526000512` (*Scanlan v. Coalition for Open Democracy*, 26A512, granted after response and referral to full Court) and `scotus/9526000476` (*FCC v. Brown*, 26A476, federal applicant, granted after response and referral to full Court), plus 8 granted cert petitions.

## 2. CourtListener MCP Calls

1. **`mcp_courtlistener_search` (opinions):**
   - Query: `type="o"`, `q=""Denise Smith" "Brown, Savage" OR "Stitely""`
   - Result: 161 general hits (`query_id: "b96b0c6f"`); none matched this party pair.
2. **`mcp_courtlistener_search` (RECAP):**
   - Query: `type="r"`, `q=""Denise Smith" "Stitely" OR "Britto""`
   - Result: 3,405 hits (`query_id: "f06908e2"`), including `Smith v. Nationstar Mortgage LLC`, Docket No. `8:25-cv-02817` (D. Md.), listing Document 59 (`recap_document_id: 496317114`), a Memorandum Opinion filed October 5, 2026.
3. **`mcp_courtlistener_search` (opinions):**
   - Query: `type="o"`, `q=""Stitely" AND "Callahan""`
   - Result: 1 unrelated California opinion (`People v. Johnson`).
4. **`mcp_courtlistener_search` (RECAP):**
   - Query: `type="r"`, `q=""Stitely" AND "Callahan""`
   - Result: 19 RECAP dockets (`query_id: "0cc347c2"`), including `Smith v. Nationstar Mortgage LLC` (D. Md. `8:25-cv-02817`) and several other Maryland foreclosure/bankruptcy dockets involving substitute trustees from `Brown, Savage, Britto, Stitely and Callahan`.
5. **`mcp_courtlistener_read_document`:**
   - Parameters: `recap_document_id=496317114`
   - Result: Read the full 21-page Memorandum Opinion (48,380 chars) by Chief Magistrate Judge Timothy J. Sullivan in *Denise R. Smith v. Nationstar Mortgage LLC, et al.*, Case No. 8:25-cv-02817-TJS (D. Md. Oct. 5, 2026), detailing the Prince George's County foreclosure (`CAEF17-36003`), the Bankruptcy Court orders (`18-20825`), the Appellate Court of Maryland's April 14, 2026 dismissal of `ACM-REG-1051-2025` for failure to file a compliant brief, the Supreme Court of Maryland's denial of certiorari in No. 119, and the dismissal of Smith's federal foreclosure/possession claims under *Rooker-Feldman* and *res judicata*.

## 3. Web Search (`google_web_search`)

1. **`google_web_search`:**
   - Query: `"Brown, Savage, Britto, Stitely" OR "Stitely & Callahan" Maryland "Denise Smith"`
   - Result: Confirmed the background of the Maryland foreclosure dispute over 917 Jennings Mill Drive, Bowie, MD (Prince George's County Circuit Court No. `CAEF17-36003`; Appellate Court of Maryland No. `914-2022` and `1051-2025`; Supreme Court of Maryland Petition No. `119`; D. Md. No. `8:25-cv-02817`) and that Application `26A619` was submitted to Chief Justice Roberts on October 27, 2026, and docketed on October 30, 2026 (no disposition reported).
