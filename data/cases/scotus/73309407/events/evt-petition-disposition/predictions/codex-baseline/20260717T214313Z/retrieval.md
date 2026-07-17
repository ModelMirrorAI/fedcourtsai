# Retrieval beyond the provisioned inputs

## Corpus base rates

- Consulted `metrics/statpack.md`, especially "Modern discretionary-cert petitions by disposition," "Cert petitions by relist count," "Cert petitions by CVSG status," and the 2025-Term row.
- Consulted the 2025-Term paid-fee-class detail in `metrics/statpack.json` (estimated paid-petition grant rate 5.36%).
- No `fedcourts query` or `fedcourts open-events` corpus lookup was made, so there is no ranged-read line to report.

## CourtListener MCP searches

All searches were opinion searches. None sought this case or its disposition.

1. `q="28 U.S.C. 1257 final judgment interlocutory state criminal prosecution"`, `court=scotus`, 5 results. This surfaced finality authorities including *Pennsylvania v. Ritchie* and *Fort Wayne Books*.
2. `q="THC marijuana driving impairment due process vagueness under the influence"`, all courts, 5 results. This returned state impaired-driving cases but no persuasive Supreme Court conflict.
3. `q="capable of repetition yet evading review criminal prosecution mootness"`, `court=scotus`, 5 results. This surfaced *United States v. Sanchez-Gomez*, 584 U.S. 381 (2018), and other mootness authorities.
4. `citation="420 U.S. 469"`, 3 results. Citation matching was noisy and did not return *Cox Broadcasting* in the first page.
5. `citation="522 U.S. 75"`, 3 results. Citation matching was noisy and did not return *Jefferson* in the first page.
6. `citation="584 U.S. 381"`, 3 results. This returned *United States v. Sanchez-Gomez*.
7. `case_name="Cox Broadcasting Corp. v. Cohn"`, `court=scotus`, 5 results. This returned *Cox Broadcasting Corp. v. Cohn*, 420 U.S. 469 (1975), and its opinion metadata.
8. `case_name="Jefferson v. City of Tarrant"`, `court=scotus`, 5 results. This returned *Jefferson v. City of Tarrant*, 522 U.S. 75 (1997), whose lead-opinion snippet describes the pending state matter as brought too soon.

No web searches were used.
