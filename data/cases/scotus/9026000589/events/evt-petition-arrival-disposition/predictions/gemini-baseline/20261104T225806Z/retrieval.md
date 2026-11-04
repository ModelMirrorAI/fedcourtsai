# Prior Retrieval Log

## 1. Corpus Queries (`fedcourts query`)

### Query 1: Related Pending Cert Petition (`Trump v. Thakur`, No. 26-210)
- **Command:** `uv run fedcourts query --court scotus --docket-number 26-210`
- **Transfer:** `ranged corpus reads: 14 GET(s), 3670016 byte(s)`
- **Filters:** `--court scotus`, `--docket-number 26-210`
- **Priors Returned:**
  - `scotus/9026000210` (`Donald J. Trump, President of the United States, et al. v. Neeta Thakur, Individually and on Behalf of All Others Similarly Situated, et al.`, No. 26-210, filed `2026-08-19`, originating court `ca9`, distributed for conference `2026-11-13`, `distribution_count: 1`, open).
- **What we took from it:** Confirmed that `Trump v. Thakur`, No. 26-210 (cited in footnote 3 and footnote 5 of the petition) is currently pending and distributed for the November 13, 2026 conference, providing context for whether `26-589` would receive plenary review (`granted`) vs. a hold/GVR (`gvr`).

### Query 2: Related Prior Proceeding in Same Controversy (`Farag v. Climate United Fund`, No. 25-48)
- **Command:** `uv run fedcourts query --court scotus --docket-number 25-48`
- **Transfer:** `ranged corpus reads: 1 GET(s), 262144 byte(s)`
- **Filters:** `--court scotus`, `--docket-number 25-48`
- **Priors Returned:**
  - `scotus/73272783` (`Tarek Farag v. Climate United Fund, et al.`, No. 25-48, originating court `cadc` Nos. 25-5122, 25-5123, `disposition: denied` on `2025-10-06`).
- **What we took from it:** Confirmed that the earlier related docket No. 25-48 was an ancillary/intervenor petition filed by a private individual (`Tarek Farag`) at an earlier stage of the litigation and denied in October 2025, having no negative bearing on the Solicitor General's cert petition following the August 2026 en banc judgment.

### Query 3: Recent Granted SCOTUS Cases in the 2020s Era
- **Command:** `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
- **Transfer:** `ranged corpus reads: 33 GET(s), 8650752 byte(s)`
- **Filters:** `--court scotus`, `--era 2020s`, `--disposition granted`, `--limit 10`
- **Priors Returned:**
  - `scotus/9026000204` (`Department of Justice, et al. v. Scott McNutt, et al.`, No. 26-204, cert granted `2026-10-19`, `distribution_count: 2`, SG petitioner from `ca5`)
  - `scotus/73281386` (`U.S. DOGE Service, et al. v. United States District Court for the District of Columbia, et al.`, No. 25-1103, cert granted `2026-10-13`, `distribution_count: 2`, SG petitioner from `cadc`)
  - `scotus/73500246` (`Todd Blanche, Attorney General v. Izuchukwu Ozurumba`, No. 25-1343, cert granted `2026-10-13`, `distribution_count: 2`, SG petitioner from `ca4`)
  - `scotus/9026000104` (`Philip L. Rhoney, Acting Director of the Buffalo Field Office of U.S. Immigration and Customs Enforcement v. Ricardo Aparecido Barbosa da Cunha`, No. 26-104, cert granted `2026-10-01`, `distribution_count: 1`, SG petitioner from `ca2`)
  - Plus recent private-party grants (`26-12`, `25-7026`, `25-1131`, `25-1349`) and interim application grants (`26A512`, `26A476`).
- **What we took from it:** Reinforced the statpack's high grant rate for Solicitor General petitions (`federal` band), including recent OT2026 grants from the D.C. Circuit and other circuits on executive-branch institutional and statutory litigation.

## 2. Open-Web / CourtListener MCP Lookups

- **Tool:** `mcp_courtlistener_search` (`type="d"`, `court="scotus"`, `case_name="Thakur"`) — 0 SCOTUS RECAP docket results.
- **Tool:** `mcp_courtlistener_search` (`type="o"`, `case_name="Sustainability Institute"`) — returned `The Sustainability Institute v. Donald Trump`, No. 25-1575 (`ca4`, filed `2026-01-21`), confirming the Fourth Circuit parallel grant-termination precedent cited in the petition.
