corpus queries:
- `uv run fedcourts query --court scotus --include-applications "religious freedom stay state court injunction" --limit 5` (Failed due to extra arguments)
- `uv run fedcourts query --court scotus --include-applications --limit 5`
  - `ranged corpus reads: 6 GET(s), 1441792 byte(s)`

No other retrieval beyond the provisioned inputs and the statpack.