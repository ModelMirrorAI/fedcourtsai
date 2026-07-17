# Retrieval

## Committed base rates

- Consulted `metrics/statpack.md` and `metrics/statpack.json`, including modern discretionary-cert disposition, paid-petition, relist, CVSG, and 2025 Term rates.

## Corpus lookup

- Command: `uv run fedcourts query --court scotus --citation 'Republican Party of Minnesota v. White' --citation 'Williams-Yulee v. Florida Bar' --citation 'Pickering v. Board of Education' --era 2020s --limit 12`
- Result: failed before results because the ranged corpus remote's hostname could not be resolved (`EndpointConnectionError`). No `ranged corpus reads: ...` line was emitted.

## CourtListener MCP

- Opinion search: `"sitting judge" Pickering "strict scrutiny" judicial speech`, limited to opinions filed before July 17, 2026. This identified relevant authorities including *Siefert v. Alexander*, *Mississippi Commission on Judicial Performance v. Moore*, and the provisioned Pennsylvania judgment.
- Opinion search: `judicial conduct Facebook political speech endorsement strict scrutiny Pickering`, limited to opinions filed before July 17, 2026.
- Case-name search: *Disciplinary Counsel v. Rudduck*, limited to opinions filed before July 17, 2026.
- Case-name search: *Disciplinary Counsel v. Grendell*, limited to opinions filed before July 17, 2026.
- Case-name search: *Mississippi Commission on Judicial Performance v. Moore*, limited to opinions filed before July 17, 2026.
- Opinion endpoint lookup: Ohio Supreme Court opinion in *Disciplinary Counsel v. Rudduck*, 2026-Ohio-1126 (opinion id 11299138), used to confirm its strict-scrutiny holding and Facebook/judicial-identification facts.

No web search was used. No search sought this petition's disposition or subsequent history.
