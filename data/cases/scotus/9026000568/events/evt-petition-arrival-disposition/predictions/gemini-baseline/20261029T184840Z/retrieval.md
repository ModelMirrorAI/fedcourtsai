# Retrieval Log — `scotus/9026000568` (`evt-petition-arrival-disposition`)

## 1. Local Corpus Queries (`uv run fedcourts query`)

We executed 6 `fedcourts query` commands against the local DuckDB corpus (`corpus/corpus.db`). Total transfer across all invocations: **813 GET(s), 212,926,464 byte(s)**.

### Query 1 — Lead Granted Case (*Rhoney v. Barbosa da Cunha*, No. 26-104)
- **Command**: `uv run fedcourts query --court scotus --docket-number 26-104`
- **Transfer**: `ranged corpus reads: 12 GET(s), 3145728 byte(s)`
- **Filters**: `court=scotus`, `docket_number=26-104`
- **Results & Utility**:
  - `scotus/9026000104` (*Philip L. Rhoney, Acting Director of the Buffalo Field Office of U.S. Immigration and Customs Enforcement v. Ricardo Aparecido Barbosa da Cunha*, No. 26-104): Filed `2026-07-23`, distributed `2026-09-28` (`distribution_count = 1`), cert granted `2026-10-01` (`disposition = "granted"`), originating from the Second Circuit (`ca2`, docket `25-3141`), with Solicitor General D. John Sauer as counsel of record for petitioner. Directly confirmed the lead case cited in the SG's hold request in No. 26-568.

### Query 2 — Recent SCOTUS GVR Dispositions (`2020s` Era)
- **Command**: `uv run fedcourts query --court scotus --disposition gvr --era 2020s --limit 5`
- **Transfer**: `ranged corpus reads: 27 GET(s), 7077888 byte(s)`
- **Filters**: `court=scotus`, `disposition=gvr`, `era=2020s`, `limit=5`
- **Results & Utility**:
  - Returned 5 OT 2026 GVR cases (`scotus/73317900` *Burford German Funding LLC v. financialright claims GmbH*, No. 25-1269; `scotus/73500268` *Roofing Designs by JR v. Royal American Construction*, No. 25-1367; `scotus/73500579` *Silva Ochoa v. United States*, No. 25-7569; `scotus/9026000139` *Monsanto Co. v. Dennis*, No. 26-139; `scotus/9026005216` *Hobson v. United States*, No. 26-5216). Confirmed how `disposition = "gvr"` is recorded in the OT 2026 forward ledger and how distribution counts (`1` to `2+`) behave on GVR dispositions.

### Query 3 — Recent SCOTUS Granted Dispositions (`2020s` Era)
- **Command**: `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 5`
- **Transfer**: `ranged corpus reads: 0 GET(s), 0 byte(s)`
- **Filters**: `court=scotus`, `disposition=granted`, `era=2020s`, `limit=5`
- **Results & Utility**:
  - Returned recent OT 2026 grants including Solicitor General petitions `scotus/9026000204` (*Department of Justice v. McNutt*, No. 26-204, `distribution_count = 2`) and `scotus/73281386` (*U.S. DOGE Service v. U.S. District Court for the District of Columbia*, No. 25-1103, `distribution_count = 2`). Provided context on SG cert grants in OT 2026.

### Query 4 — Recent OT 2026 Open and Resolved SCOTUS Cases
- **Command**: `uv run fedcourts query --court scotus --include-open --era 2020s --limit 30`
- **Transfer**: `ranged corpus reads: 0 GET(s), 0 byte(s)`
- **Filters**: `court=scotus`, `include_open=True`, `era=2020s`, `limit=30`
- **Results & Utility**:
  - Surveyed 30 recent OT 2026 dockets to inspect current Term disposition patterns across paid and federal petitions.

### Query 5 — SCOTUS Priors Naming the Ninth Circuit Panel Judges
- **Command**: `uv run fedcourts query --court scotus --judge Bress --judge Bea --judge McKeown --limit 10`
- **Transfer**: `ranged corpus reads: 641 GET(s), 167837696 byte(s)`
- **Filters**: `court=scotus`, `judge=[Bress, Bea, McKeown]`, `limit=10`
- **Results & Utility**:
  - Returned 0 rows because SCOTUS rows do not populate lower-court panel judges in the `judges`/`panel` field.

### Query 6 — Ninth Circuit Priors Naming Judge Bress
- **Command**: `uv run fedcourts query --court ca9 --judge Bress --limit 5`
- **Transfer**: `ranged corpus reads: 133 GET(s), 34865152 byte(s)`
- **Filters**: `court=ca9`, `judge=[Bress]`, `limit=5`
- **Results & Utility**:
  - Returned 0 rows in the filtered slice; the full text of Judge Bress's majority opinion and Judge Bea's dissent in *Rodriguez Vazquez v. Bostock* (No. 25-6842) was already provisioned in full in `data/cases/scotus/9026000568/record/documents/petition.txt` (App. 1a–94a).

---

## 2. CourtListener MCP Lookups

We executed 6 `mcp_courtlistener_search` calls (the first 3 parallel calls returned HTTP 429 rate-limit responses with a 180-second cooldown; the subsequent 3 calls after the window succeeded):

1. **Ninth Circuit Decision Below (*Rodriguez Vazquez v. Bostock*)**:
   - **Tool**: `mcp_courtlistener_search(type="o", case_name="Rodriguez Vazquez v. Bostock")`
   - **Result**: `cluster_id = 10936657` — *Rodriguez Vazquez v. Bostock*, No. 25-6842 (9th Cir. filed July 30, 2026). Confirmed metadata matching the provisioned petition appendix.
2. **Second Circuit Lead Case Decision (*Barbosa da Cunha v. Freden*)**:
   - **Tool**: `mcp_courtlistener_search(type="o", case_name="Barbosa da Cunha v. Freden")`
   - **Result**: `cluster_id = 10983473` — *Barbosa Da Cunha v. Freden*, No. 25-3141 (2d Cir. filed Sept. 25, 2026). Confirmed the Second Circuit decision underlying *Rhoney v. Barbosa da Cunha*, No. 26-104.
3. **Fifth Circuit Split Decision (*Buenrostro-Mendez v. Bondi*)**:
   - **Tool**: `mcp_courtlistener_search(type="o", case_name="Buenrostro-Mendez v. Bondi")`
   - **Result**: `0` matches under exact hyphenated caption search; the opinion's reasoning and citations (`166 F.4th 494 (5th Cir. 2026)`) were thoroughly detailed in the provisioned Ninth Circuit opinion (`petition.txt` at 17a, 25a–26a, 35a, 37a, 43a, 46a–47a, 49a).
