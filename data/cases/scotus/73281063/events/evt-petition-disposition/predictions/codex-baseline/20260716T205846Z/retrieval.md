# Retrieval

## Committed base rates

- Consulted `metrics/statpack.md`, especially “Modern discretionary-cert petitions by disposition,” “Modern cert petitions by originating circuit,” “Cert petitions by relist count,” and the Term table.
- Consulted `metrics/statpack.json` for the Term 2025 paid-petition estimate (5.36% grant rate).

## Corpus query

- Attempted: `uv run fedcourts query --court scotus --citation 'Summers v. Earth Island Institute' --citation 'Brnovich v. Democratic National Committee' --citation 'Village of Arlington Heights v. Metropolitan Housing Development Corp.' --era 2020s --limit 10 --corpus-backend ranged`
- Result: failed before any corpus rows were returned because the remote corpus host could not be resolved (`EndpointConnectionError`). No `ranged corpus reads` line was printed.

## CourtListener MCP

- Opinion search: `associational standing identified member Summers organizational plaintiff`, restricted to SCOTUS opinions filed before July 17, 2026. The results included *Summers v. Earth Island Institute*, *FDA v. Alliance for Hippocratic Medicine*, and *Clapper v. Amnesty International USA*.
- Opinion search: `legislative good faith discriminatory intent clear error election Arlington Heights Brnovich`, restricted to SCOTUS opinions from January 1, 2020 through July 16, 2026. The results included *Brnovich v. Democratic National Committee* and *Allen v. Milligan*.

Neither MCP search queried this case, its docket number, its disposition, or its subsequent history.
