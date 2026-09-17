# Retrieval log

## Committed context

- Read `metrics/statpack.md`: modern-cert disposition/circuit context, paid-segment relist and CVSG cuts, and the `sal-v4` reached-rate table. Used only Terms 2017–2024 for the grant anchor. A local arithmetic calculation of the displayed baseline reached rates and denominators returned approximately 5.1203%, weighted n=11,580.
- Inspected top-level keys of `metrics/statpack.json` for metadata; no additional quantitative estimate was taken from it. These are the committed artifacts available in this checkout, not a live corpus refresh.
- No `fedcourts query` or `open-events` lookup was made, so there is no ranged-corpus transfer line to report. `fedcourts paths --court scotus --docket 73344703 --event evt-petition-disposition --role predictor` resolved the event location. Its first invocation failed because the default uv cache was read-only; retrying with a writable temporary cache succeeded.

## Web attempts: no usable content returned

1. A combined search requested `site.supremecourt.gov Rule 10 writ certiorari erroneously factual findings misapplication properly stated rule law` and `site.supremecourt.gov Manhattan Community Access Halleck 2019 private entity state actor First Amendment`. No visible results were returned.
2. Three open attempts requested `https://www.supremecourt.gov/filingandrules/rules_guidance.aspx`. All returned no visible page content.
3. A find attempt for `misapplication` at the guessed address `https://www.supremecourt.gov/filingandrules/2026RulesoftheCourt_WEB.pdf` returned no visible content. The address was not verified and was not used as authority.

None of those web attempts searched the subject case, and none supplied outcome material or evidence used in the forecast.

## CourtListener MCP: general precedent only

1. `search(type="o", citation="572 U.S. 650", num_results=1)` returned *Tolan v. Cotton*, decided May 5, 2014; opinion ID 2672535.
2. `search_document(opinion_id=2672535, query="Rule 10", snippet_size=1500)` returned the summary vacatur/remand and Justice Alito's concurrence discussing the narrow error-correction role.
3. `search_document(opinion_id=2672535, query="1983", snippet_size=700)` confirmed the federal excessive-force and qualified-immunity posture.
4. `search(type="o", case_name="Manhattan Community Access Corp. v. Halleck", court="scotus", num_results=1)` returned the June 17, 2019 opinion, reported at 587 U.S. 802, opinion ID 4407340, including its opening state-action discussion.
5. `search_document(opinion_id=4407340, query="compels", snippet_size=800)` returned the discussion of limited circumstances in which private action may be attributable to government.

No lookup targeted this petition's disposition, subsequent history, or another predictor's output. No outcome-revealing material for this petition was encountered.
