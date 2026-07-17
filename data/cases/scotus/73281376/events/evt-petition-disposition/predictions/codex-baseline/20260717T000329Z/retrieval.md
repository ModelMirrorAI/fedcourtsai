# Retrieval beyond provisioned inputs

## Committed base rates

- Consulted `metrics/statpack.md` and the 2025 Term paid-fee detail in `metrics/statpack.json`: paid petition grant rate 5.36%; modern Fourth Circuit grant rate 4.6%; no-CVSG grant rate 3.0%; zero-relist grant rate 0.8%.

## Corpus lookup

- Command: `uv run fedcourts query --court scotus --citation '436 U.S. 658' --era 2020s --limit 10 --corpus-backend ranged`
- Result: failed before reading the remote corpus because the runner could not resolve the corpus-store hostname. No `ranged corpus reads: ...` line was emitted and no priors were returned.

## CourtListener MCP

- Opinion search: type `o`; query `Monell "contracting out" medical care final policymaking authority county`; filed before `2026-07-17`; 10 results requested. The results included *Daniel v. Cook County*, 833 F.3d 728 (7th Cir. 2016), *Leach v. Shelby County*, 891 F.2d 1241 (6th Cir. 1990), and *Lee v. Milwaukee County* (7th Cir. May 7, 2026). The search was used only to assess the claimed doctrinal split and did not seek this case's disposition or subsequent history.

No web searches were used.
