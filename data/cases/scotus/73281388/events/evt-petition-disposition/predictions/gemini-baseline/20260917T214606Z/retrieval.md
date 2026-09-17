* `cat metrics/statpack.md` to retrieve the latest base rates for `relist_bucket` and `salience_band` segments (Term 2024 and earlier).
* `uv run fedcourts query --court scotus --decided-before 2026-09-17 "administrative search GPS Jones"` (Attempted, but failed due to invalid arguments as free text is not supported).
* `mcp_courtlistener_search` with query `"Johnson v. Wilson"` to search for the First Circuit decision.
* Read `context.json`, `event.yaml`, `snapshots/2026-09-17.json`, and `documents.json` from the provisioned inputs.
* Read `questions-presented.txt`, `petition.txt`, and `brief-in-opposition.txt` from the provisioned documents.
