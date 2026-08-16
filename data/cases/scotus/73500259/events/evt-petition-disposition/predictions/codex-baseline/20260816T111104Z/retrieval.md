# Retrieval

- Consulted `metrics/statpack.md` and `metrics/statpack.json`. The applicable sal-v3 elevated-band, prior-Term risk set pooled to 693 / 3,419 = 20.2691%. No `fedcourts query` or `fedcourts open-events` command was used, so there is no `ranged corpus reads:` line.
- CourtListener MCP opinion search: `q='"Motorola Mobility" FTAIA negotiations foreign purchasers'`, opinion collection, filed before 2026-08-17, eight results. It surfaced *Motorola Mobility LLC v. AU Optronics Corp.*, *Seagate Technology LLC v. NHK Spring Co.*, *United States v. Hui Hsiung*, and *Lotes Co. v. Hon Hai Precision Industry Co.*
- CourtListener MCP document searches on the result labeled as opinion 10771069 for `Motorola`, `unique`, and `proximate`. Each returned no match.
- CourtListener MCP read of purported opinion 10771069, chunks 0-2. The text was an unrelated Idaho parental-rights opinion, so it was treated as a bad link/index association and was not used.
- CourtListener MCP opinion search: `q='"Foreign Trade Antitrust Improvements Act" OR FTAIA'`, Supreme Court only, filed before 2026-08-17, ten-result limit. It returned six records, including *F. Hoffmann-La Roche Ltd. v. Empagran S.A.*, *Hartford Fire Insurance Co. v. California*, and *RJR Nabisco, Inc. v. European Community*.
