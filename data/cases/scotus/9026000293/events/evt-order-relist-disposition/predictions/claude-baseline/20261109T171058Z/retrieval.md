# Retrieval log
- Read `metrics/statpack.md` (sections on modern cert, circuits, relist, CVSG, amicus, bands, and sal-v8 band by Term).
- `uv run fedcourts query --help`
- `uv run fedcourts query --court scotus --disposition gvr --era modern --limit 5`: printed the usage text (the flag was not accepted).
- `uv run fedcourts query --court scotus --disposition gvr --limit 5`: returned 5 GVR priors, none closely analogous.
  `ranged corpus reads: 37 GET(s), 9699328 byte(s)`
- WebSearch (standard): "Havlish v. Taliban Supreme Court petition 26-292 Da Afghanistan Bank Cimex". Results covered background on the CA2 decision and the Havlish motion for a supplemental brief answering the Faiq amicus brief. Nothing reported a disposition of this petition.
- No CourtListener MCP calls.
