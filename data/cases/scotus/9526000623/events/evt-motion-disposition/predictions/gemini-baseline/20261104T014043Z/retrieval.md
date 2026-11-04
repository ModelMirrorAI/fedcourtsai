# Retrieval Log: `scotus/9526000623` (`evt-motion-disposition`)

## 1. Corpus Queries (`fedcourts query`)

1. **Command:**
   `uv run fedcourts query --court scotus --docket-number 26-6013`
   - **Stderr transfer line:** `ranged corpus reads: 13 GET(s), 3407872 byte(s)`
   - **Purpose & Findings:** Looked up the companion petition for a writ of certiorari (`26-6013`, `scotus/9026006013`, *Jesse Guardado v. Florida*) referenced in the snapshot's `Links` field (`Linked with 26-6013`). Confirmed it was filed on `2026-10-30` from the Supreme Court of Florida (`SC2026-1605`) with `distribution_count: 0` and `disposition: null` as of `last_live_polled: "2026-10-31"`.

2. **Command:**
   `uv run fedcourts query --court scotus --era 2020s --limit 10`
   - **Stderr transfer line:** `ranged corpus reads: 5 GET(s), 1310720 byte(s)`
   - **Purpose & Findings:** Retrieved the 10 most recent resolved 2020s SCOTUS priors (primarily substantive interim applications in OT2026, e.g., `26A602`, `26A619`, `26A606`, `26A613`, `26A617`, `26A618`, `26A499`, `26A535`, `26A532`), all of which were denied.

3. **Command:**
   `uv run fedcourts query --court scotus --disposition denied --era 2020s --limit 25`
   - **Stderr transfer line:** `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
   - **Purpose & Findings:** Retrieved recent denied 2020s SCOTUS priors, including *William Reaves v. Florida, et al.* (`26A524`, `scotus/9526000524`, and companion cert petition `26-5865`, `scotus/9026005865`), a directly analogous Florida capital execution stay application from the Supreme Court of Florida (`SC2026-1512, SC2026-1519`) filed on `2026-10-17` and denied on `2026-10-20`.

4. **Command:**
   `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 15`
   - **Stderr transfer line:** `ranged corpus reads: 19 GET(s), 4980736 byte(s)`
   - **Purpose & Findings:** Reviewed recently granted 2020s SCOTUS substantive applications (`26A512`, `26A476`, `26A428`, `26A406`, `26A308`, `26A388`). Noted that the lone capital grant (`26A428`, *Kenneth Nelsen, Warden v. Christa Gail Pike*) was a state warden's application to vacate a lower-court stay rather than a prisoner's stay-of-execution application.

## 2. External Retrieval (CourtListener MCP)

1. **`mcp_courtlistener_search`**:
   - **Query:** `type="o"`, `court="fla"`, `q=""Jesse Guardado""`, `order_by="dateFiled desc"`, `num_results=10`
   - **Findings:** Located the Florida Supreme Court decision under review, *Jesse Guardado v. State of Florida*, No. SC2026-1605, filed October 29, 2026 (`cluster_id: 11049070`), along with Guardado's prior Florida Supreme Court decisions (`SC17-1903`, `238 So. 3d 162`; `SC17-389`, `226 So. 3d 213`; `SC12-1040`, `176 So. 3d 886`; `SC05-2035`, `965 So. 2d 108`).

2. **`mcp_courtlistener_get_endpoint_item`**:
   - **Query:** `endpoint_id="clusters"`, `item_id=11049070`, `fields=["id", "case_name", "date_filed", "sub_opinions"]`
   - **Findings:** Resolved opinion ID `11516852` for the October 29, 2026 Florida Supreme Court decision in `SC2026-1605`.

3. **`mcp_courtlistener_read_document`**:
   - **Query:** `opinion_id=11516852`, `chunk_index=0` and `chunk_index=[1, 2, 3, 4]` (`chunk_size=8000`)
   - **Findings:** Read the complete 19-page opinion of the Florida Supreme Court in *Jesse Guardado v. State of Florida*, No. SC2026-1605 (Oct. 29, 2026), affirming the summary denial of Guardado's successive Rule 3.851 postconviction motion and denying a stay of execution. Confirmed that the Florida Supreme Court rejected (1) the *Woodard* clemency challenge on the merits because Guardado received clemency review and executive clemency is discretionary, (2) the trial/postconviction IAC mitigation claims as untimely and procedurally barred under Rule 3.851(d), and (3) the due process challenge to the 31-day warrant period under settled precedent.
