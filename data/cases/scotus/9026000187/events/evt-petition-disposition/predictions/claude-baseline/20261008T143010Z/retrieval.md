# Retrieval log

## Corpus
- `uv run fedcourts query --court scotus --era 2020s --disposition granted --limit 8` → `ranged corpus reads: 28 GET(s), 7274496 byte(s)`. Returned recent OT2025/OT2026 grants and substantive applications (immigration, capital, election cases); no analogue to a §1983 jail medical-care petition, used only to confirm the query carries no subject filter on SCOTUS rows. Not relied on.

## Committed statpack
- `metrics/statpack.md`: "Modern discretionary-cert petitions by disposition"; relist-count, CVSG and salience-band cuts (paid scored segment); the per-Term "Segment base rate by salience band (sal-v4)" table, from which the `baseline` band's bracketed `reached` rate was pooled over OT2017–OT2025 (OT2026's row is empty): ≈637 grants / n=12720 ≈ 5.0%. Cert-order share of the grant family read from the modern-cert section: 577 gvr / (655 granted + 577 gvr) ≈ 47%.

## CourtListener MCP
- `search` (type opinion, court ca5, q "Congious Shaw pretrial detainee", filed after 2026-01-01) → 1 result: *Congious v. Shaw*, No. 25-10886, published, filed 2026-03-27, cluster 10826379, opinion 11293152.
- `read_document` (opinion 11293152) → full text of the Fifth Circuit opinion (Smith, J., for the court; Wiener, J., concurring in the judgment on qualified-immunity prong two).
- `search` (type docket, court scotus, q "Helphenstine") → 0 results.

## Web
- WebFetch: supremecourt.gov docket 26-187 (this case) → three entries, identical to the provisioned snapshot; no waiver, no amicus, response due Nov. 4, 2026. No disposition.
- WebSearch: "certiorari denied Kingsley pretrial detainee deliberate indifference medical care objective standard circuit split petition 2024 2025 2026" → commentary confirming repeated denials on the split; pointers to 23-210 and 23-259 filings.
- WebSearch: "Hartman v. Short" / "Jordan v. Helphenstine" certiorari → 23-259 BIO and reply; 23-210/23-260 BIO; Hartman v. Short, No. 23-1097, denied June 10, 2024.
- WebFetch: supremecourt.gov docket 23-259 (Lewis County v. Helphenstine) → waiver, three amicus briefs, distributed 11/9/2023, response requested 10/30/2023, BIO 12/28/2023, redistributed for 1/19/2024, denied 1/22/2024.
- WebFetch: supremecourt.gov docket 23-210 (Jordan v. Howell) → waiver, distributed 10/27/2023, response requested 10/16/2023, BIO 12/15/2023, redistributed for 1/19/2024, held in abeyance on joint motion, dismissed under Rule 46 on 9/11/2024.
- WebSearch: "Short v. Hartman" Supreme Court petition → No. 23-1097.
- WebFetch: supremecourt.gov docket 23-1097 (Hartman v. Short) → one amicus (National Sheriffs' Association), distributed 6/6/2024, denied 6/10/2024; no response requested.
- WebSearch: OT2026 pending petitions on the Kingsley medical-care question → nothing found pending or granted; only background commentary.

No search surfaced a disposition of this petition; none exists as of the snapshot.
