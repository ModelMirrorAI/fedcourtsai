# Retrieval Log
- Checked statpack `metrics/statpack.md` using `grep` for "Segment base rate by salience band", "Cert petitions by relist count", and "Cert petitions by CVSG status".
- Used `mcp_courtlistener_call_endpoint` / `curl` on CourtListener to search for "Pestarino", which yielded unrelated cases from 1980s.
- Used `mcp_courtlistener_get_endpoint_item` for `dockets` ID 73292885 which returned `Roy J. Meidinger v. Commissioner of Internal Revenue` (mismatched with corpus snapshot).
No other external retrieval was used beyond the provisioned inputs and base rates.