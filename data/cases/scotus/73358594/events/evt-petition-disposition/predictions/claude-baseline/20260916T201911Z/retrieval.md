# Retrieval log

Beyond the provisioned inputs (`record/snapshots/2026-09-16.json`, `record/context.json`, `record/documents/questions-presented.txt`, `record/documents/petition.txt`, `record/documents/documents.json`, `event.yaml`) and the committed `metrics/statpack.md`:

## CourtListener MCP

1. `search(type=d, court=scotus, q="Whistleblower Protection Act" OR "2302(b)(8)", filed_after=2025-06-01, order_by=dateFiled desc, num_results=15)` — purpose: check for pending or companion SCOTUS petitions on the same provision (hold-candidate check). Result: 0 dockets (CourtListener carries few SCOTUS dockets).
2. `search(type=o, court=scotus, q="2302(b)(8)" OR "Whistleblower Protection Act" OR "Merit Systems Protection Board", filed_after=2024-01-01, order_by=dateFiled desc, num_results=15)` — purpose: check for an intervening SCOTUS decision that could make this a GVR vehicle. Result: 18 hits, newest Margolin v. NAIJ (25-767, 2026-05-26), then Riley v. Bondi, Feliciano v. Department of Transportation, Corner Post, SEC v. Jarkesy, Harrow v. Department of Defense. None read; none recognized as bearing on the reasonable-belief analysis under § 2302(b)(8)(A).

## Corpus tooling

No `fedcourts query` or `open-events` calls (no `ranged corpus reads` line to record). `uv run fedcourts paths --court scotus --docket 73358594 --event evt-petition-disposition --role predictor` was run to resolve paths only.

## Web

No web searches.
