# Retrieval log

Beyond the provisioned inputs (snapshot, context, event, QP, petition, both briefs in opposition) and the committed `metrics/statpack.md`:

1. `uv run fedcourts paths --court scotus --docket 73266074 --event evt-petition-disposition --role predictor` (path resolution only).
2. `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8`
   stderr: `ranged corpus reads: 11 GET(s), 2752512 byte(s)`
   Result: eight rows, almost all substantive applications (DHS v. D.V.D., People Not Politicians v. Onder, NRCC v. Brown, and similar); not useful as cert-petition priors for this case and not relied on.
3. CourtListener MCP `search` (type `d`, court `scotus`, q `"Hastings College Conservation Committee"`): 0 results. No docket row exists there for No. 25-1231.
4. Web search: `"Hastings College Conservation Committee" Supreme Court certiorari 25-1231 Contract Clause bill of attainder`. Results: the supremecourt.gov docket page and a July 2026 extension letter, the California Court of Appeal opinions (2023 anti-SLAPP appeal, 2025 merits appeal) on Justia and CourtListener, 2023 news on the California Supreme Court's denial of review, and the Center for American Liberty's case page. Nothing postdating the snapshot and nothing outcome-revealing.
