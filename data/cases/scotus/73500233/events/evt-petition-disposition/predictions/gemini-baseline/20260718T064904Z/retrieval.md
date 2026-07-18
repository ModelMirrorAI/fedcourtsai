- `cat metrics/statpack.md | grep -A 40 "Modern discretionary-cert petitions by disposition"`
- `cat metrics/statpack.md | grep -A 20 "Cert"`
- `cat data/cases/scotus/73500233/record/documents/petition.txt | grep -i "reasons for granting the writ" -A 100`
- `cat data/cases/scotus/73500233/record/documents/petition.txt | grep -i -C 3 "split "` (no results)
- `cat data/cases/scotus/73500233/record/documents/petition.txt | grep -i -E "conflict|divided|diverge"` (no results)

No retrieval from `fedcourts query` (a syntax error occurred and I relied on the explicit text in the petition confirming no clear legal precedent) or the CourtListener MCP server (not necessary as the case's posture and petition text are conclusive).
