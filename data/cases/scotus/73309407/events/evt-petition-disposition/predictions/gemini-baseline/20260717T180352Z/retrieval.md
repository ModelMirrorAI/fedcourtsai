- Consulted metrics/statpack.md to establish the baseline grant rate for modern discretionary-cert dockets.
- Attempted to query the corpus via fedcourts query (topic "THC") but topics are not available for SCOTUS dockets:
  uv run fedcourts query --court scotus --topic "THC"
  ranged corpus reads: 464 GET(s), 121503744 byte(s)
  note: topic filter: 0 of 589685 rows in scope (scotus) carry a topic...
- Read the provisioned snapshot and document inputs. No additional MCP queries were made as the case specifics strongly indicated a denial based on procedural posture (no response filed, highly fact-bound questions presented).
