# Retrieval Log

I used `fedcourts query` to retrieve similar denied petitions, though this case is heavily fact-bound and pro se.
`uv run fedcourts query --court "scotus" --disposition "denied" --limit 3`
`ranged corpus reads: 201 GET(s), 52559872 byte(s)`

I used `cat metrics/statpack.md | grep -A 20 "Modern discretionary-cert petitions"` to retrieve the base rates for modern cert petitions (overall and by circuit, though this originates from state court, which is also generally very low).

I used `grep -i "fee" metrics/statpack.md -B 2 -A 10` to retrieve base rates for paid vs. IFP cases, which highlighted a 2.5% grant rate for Paid cases in the most recent term.

I used `grep -i "relist" metrics/statpack.md -B 2 -A 10` to retrieve base rates by relist count, finding that 0-relist petitions have a grant rate of 0.8%.
