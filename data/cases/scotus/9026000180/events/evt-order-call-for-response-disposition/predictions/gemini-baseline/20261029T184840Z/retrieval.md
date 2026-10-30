# Retrieval Log

- **Case ID**: `scotus/9026000180`
- **Event ID**: `evt-order-call-for-response-disposition`
- **Predictor ID**: `gemini-baseline`
- **Run ID**: `20261029T184840Z`
- **Mode**: `forward` (`cutoff: 2026-09-18`, `decided_before: null`)

---

## 1. Corpus Base Rates (`metrics/statpack.md`)

Read `metrics/statpack.md` directly to anchor the prediction on the committed SCOTUS cert-stage base rates:
- **Segment base rate by salience band (`sal-v4`)**: For `baseline` paid petitions, the `[reached]` risk-set grant-family rate is `4.0%` in OT2025 ($n=1{,}314$), `5.9%` in OT2024 ($n=1{,}274$), `5.9%` in OT2023 ($n=1{,}312$), `5.9%` in OT2022 ($n=1{,}196$), and `5.7%` in OT2021 ($n=1{,}500$), while terminal `baseline` is `0.6%–1.9%` and terminal `elevated` is `7.8%–13.4%`.
- **Originating circuit (`ca9`)**: Paid discretionary-cert petitions from the Ninth Circuit resolve at `denied 94.8%, granted 2.1%, dismissed 1.9%, gvr 1.1%` ($n=5{,}577$).
- **Cert amicus count (`2+`)**: Paid petitions with 2+ cert-stage amicus briefs resolve at `denied 76.0%, granted 18.4%, gvr 4.5%, dismissed 1.2%` ($n=1{,}449$).

---

## 2. Corpus Queries (`uv run fedcourts query`)

### Query 1: Recent 2020s SCOTUS Granted Priors
- **Command**: `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
- **Transfer stats**: `ranged corpus reads: 34 GET(s), 8716288 byte(s)`
- **Returned priors & what was used**:
  - `scotus/9026000012` (*Association for Education Fairness v. Montgomery County Board of Education*, No. 26-12): Granted 2026-10-19 after 3 distributions (`salience_score: 0.4194`). Contrasted with the present case as an example of a clean, preserved institutional policy challenge with multiple relists that secured a grant.
  - `scotus/73281619` (*Missionaries of Saint John the Baptist, Inc. v. Frederic*, No. 25-1131): Granted 2026-10-01 after 2 distributions (`salience_score: 0.083`), where Gene C. Schaerr also appeared as amicus counsel.
  - `scotus/9026000204` (*Department of Justice v. McNutt*, No. 26-204), `scotus/73281386` (*U.S. DOGE Service v. U.S. District Court*, No. 25-1103), `scotus/73500246` (*Blanche v. Ozurumba*, No. 25-1343), `scotus/9026000104` (*Rhoney v. Barbosa da Cunha*, No. 26-104): Federal-petitioner grants illustrating the dominance of Solicitor General petitions in the granted cohort.

### Query 2: Related Parental-Rights / Gender-Transition Petition Cited in Petition (No. 25-89)
- **Command**: `uv run fedcourts query --court scotus --docket-number 25-89`
- **Transfer stats**: `ranged corpus reads: 10 GET(s), 2621440 byte(s)`
- **Returned prior & what was used**:
  - `scotus/71639365` (*Jonathan Lee, et al. v. Poudre School District R-1*, No. 25-89): Originating from CA10 (`24-1254`), filed 2025-07-23, distributed twice (`distribution_count: 2`, `salience_score: 0.1025`), **denied** on 2025-10-14 (with a statement respecting denial by Justice Alito, joined by Justices Thomas and Gorsuch, `146 S. Ct. 26`). Directly used in `reasoning.md` to show that even cleaner parental-rights challenges involving school gender-transition policies (including shared amicus counsel David Anthony Dalia / America's Frontline Doctors) were denied certiorari after multiple distributions.

### Query 3: Ninth Circuit Panel Judges (`Sidney R. Thomas`, `Jacqueline H. Nguyen`, `Daniel P. Bress`)
- **Command**: `uv run fedcourts query --court scotus --judge "Sidney R. Thomas" --judge "Jacqueline H. Nguyen" --judge "Daniel P. Bress" --limit 10`
- **Transfer stats**: `ranged corpus reads: 641 GET(s), 167837696 byte(s)`
- **Returned priors**: 0 matching SCOTUS rows (panel judge metadata is unpopulated on most SCOTUS cert rows).

### Query 4: Citation Lookup in Corpus
- **Command**: `uv run fedcourts query --court scotus --citation "145 S. Ct. 14" --citation "146 S. Ct. 26" --citation "146 S. Ct. 926" --citation "607 U.S. 492" --limit 10`
- **Transfer stats**: `ranged corpus reads: 7 GET(s), 1835008 byte(s)`
- **Returned priors**: 0 rows (parallel reporter citations are sparsely populated in the cert table; `25-89` was retrieved by `--docket-number` in Query 2).

### Query 5: Recent 2020s SCOTUS Denied and GVR Priors
- **Command**: `uv run fedcourts query --court scotus --era 2020s --disposition denied --limit 10` and `uv run fedcourts query --court scotus --era 2020s --disposition gvr --limit 5`
- **Transfer stats**: `ranged corpus reads: 2 GET(s), 524288 byte(s)` and `ranged corpus reads: 1 GET(s), 262144 byte(s)`
- **Returned priors & what was used**:
  - Examined recent OT2026 denials (`scotus/9026005865`, `scotus/9526000499`, `scotus/9526000416`) and GVRs (`scotus/73317900` *Burford German Funding*, `scotus/73500268` *Roofing Designs*, `scotus/9026000139` *Monsanto v. Dennis*) to confirm typical distribution counts (`distribution_count: 2`) and profiles for GVR dispositions.

---

## 3. CourtListener MCP Tools

- **Local Citation Extraction (`mcp_courtlistener_extract_citations`)**:
  - Extracted and verified citation structure for the eight principal Supreme Court authorities discussed in the petition: *Mirabelli v. Bonta*, 607 U.S. 492 (2026); *Zorn v. Linton*, 146 S. Ct. 926 (2026); *Lee v. Poudre Sch. Dist. R-1*, 146 S. Ct. 26 (2025); *Parents Protecting Our Child., UA v. Eau Claire Area Sch. Dist.*, 145 S. Ct. 14 (2024); *Baxter v. Bracey*, 590 U.S. 1011 (2020); *Hoggard v. Rhodes*, 141 S. Ct. 2421 (2021); *Carroll v. Carman*, 574 U.S. 13 (2014); and *Hope v. Pelzer*, 536 U.S. 730 (2002).
- **CourtListener Opinion Search (`mcp_courtlistener_search`)**:
  - Attempted three opinion searches (`Mirabelli v. Bonta`, `Zorn v. Linton`, `Lee v. Poudre School District`), which returned `HTTP 429: Request was throttled. Rate limit exceeded: 1400/day`. Because the full petition, lower court opinions (9th Cir. memorandum opinion, N.D. Cal. orders, and 9th Cir. en banc denial order), and family court custody order were already provisioned in `record/documents/petition.txt`, and `Lee v. Poudre School District` (No. 25-89) was retrieved from the local corpus via `fedcourts query --docket-number 25-89`, the upstream CourtListener rate limit did not impair the analysis.
