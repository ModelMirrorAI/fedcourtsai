# Retrieval Log

## Corpus Queries (`uv run fedcourts query`)

1. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 10`
   - Transfer: `ranged corpus reads: 38 GET(s), 9961472 byte(s)`
   - Result: Returned 10 recent OT2026 SCOTUS granted petitions and applications (including `scotus/9026000012`, `scotus/9026000204`, `scotus/73281386`, `scotus/73283862`, `scotus/73500246`, `scotus/73281619`, `scotus/73500251`, `scotus/9026000104`).

2. `uv run fedcourts query --court scotus --docket-number 25-1`
   - Transfer: `ranged corpus reads: 11 GET(s), 2883584 byte(s)`
   - Result: Returned `scotus/73110505` (*James Skinner v. Louisiana*, No. 25-1), a Louisiana post-conviction *Brady* petition supported by several of the same amici (Innocence Network, Cato Institute, Evan Bergeron, law professors) that was relisted (`distribution_count: 9`) and denied on `2026-03-30`.

3. `uv run fedcourts query --court scotus --docket-number 22-77`
   - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned `scotus/67123792` (*David Brown v. Louisiana*, No. 22-77), a Louisiana capital *Brady* petition challenging sufficiency-based materiality review that was distributed 7 times (`distribution_count: 7`) and denied on `2023-04-03`.

4. `uv run fedcourts query --court scotus --docket-number 25-51`
   - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned `scotus/72187113` (*Christopher Klein, et al. v. Charles Brandon Martin*, No. 25-51), granted and summarily reversed on `2026-01-26` after 11 distributions (`distribution_count: 11`).

5. `uv run fedcourts query --court scotus --docket-number 24-7351`
   - Transfer: `ranged corpus reads: 1 GET(s), 262144 byte(s)`
   - Result: Returned `scotus/72486825` (*Terry Pitchford v. Burl Cain*, No. 24-7351), granted `2025-12-15` and reversed `2026-05-28` (`Jo-Ann Tamila Sagar` among petitioner's counsel).

6. `uv run fedcourts query --court scotus --docket-number 26-19`
   - Transfer: `ranged corpus reads: 0 GET(s), 0 byte(s)`
   - Result: Returned `scotus/9026000019` (*Allison Nguyen v. Louisiana*, No. 26-19), a pending OT2026 petition from the Court of Appeal of Louisiana, Fifth Circuit.

## CourtListener MCP Lookups

1. `mcp_courtlistener_search(type="o", court="scotus", q=""Skinner v. Louisiana" OR "Klein v. Martin" OR "Robinson v. Louisiana"", fields=["caseName", "citation", "dateFiled", "docketNumber", "snippet"])`
   - Result: Returned 14 results, including *Klein v. Martin*, No. 25-51 (decided `2026-01-26`), *Glossip v. Oklahoma*, No. 22-7466 (`2025-02-25`), *Pitchford v. Cain*, No. 24-7351 (`2026-05-28`), *Shockley v. Vandergriff*, No. 23-7173 (`2025-03-31`), and *Brown v. Louisiana*, No. 22-77 (`2023-04-03`).

## Web Searches

- None attempted.
