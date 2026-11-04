# Retrieval Log

## Corpus Queries (`fedcourts query`)

1. `uv run fedcourts query --court scotus --docket-number 26-210`
   - Transfer: `ranged corpus reads: 14 GET(s), 3670016 byte(s)`
   - Result: Returned 1 row for `scotus/9026000210` (*Donald J. Trump, President of the United States, et al. v. Neeta Thakur, et al.*, No. 26-210, filed 2026-08-19, distributed for conference 2026-11-13, pending).

2. `uv run fedcourts query --court scotus --docket-number 25-48`
   - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned 1 row for `scotus/73272783` (*Tarek Farag v. Climate United Fund, et al.*, No. 25-48, certiorari denied 2025-10-06, prior interlocutory petition arising from the same lower-court docket).

3. `uv run fedcourts query --court scotus --era 2020s --limit 10`
   - Transfer: `ranged corpus reads: 6 GET(s), 1572864 byte(s)`
   - Result: Returned 10 recent 2020s SCOTUS priors (primarily recent OT2026 applications and petitions).

4. `uv run fedcourts query --court scotus --disposition granted --era 2020s --limit 10`
   - Transfer: `ranged corpus reads: 27 GET(s), 7077888 byte(s)`
   - Result: Returned 10 recently granted 2020s SCOTUS priors (including recent Solicitor General petitions granted in October 2026 such as *Department of Justice v. McNutt*, No. 26-204, *U.S. DOGE Service v. U.S. District Court*, No. 25-1103, *Blanche v. Ozurumba*, No. 25-1343, and *Rhoney v. Barbosa da Cunha*, No. 26-104).

## CourtListener MCP and Web Search

- No CourtListener MCP calls or external web searches were needed beyond the provisioned documents (`petition.txt`, `questions-presented.txt`, `decision-below.txt`, `lower-court-docket.txt`) and the corpus queries above.
