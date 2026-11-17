# Retrieval log

- Provisioned inputs only for the case itself: snapshot, context.json, petition/QP text, lower-court-docket.txt, related dockets 26-292 and 26-294, same-question.json (empty).
- `metrics/statpack.md`: relist-count cut, CVSG-status cut, salience band table (sal-v8).
- `uv run fedcourts paths --court scotus --docket 9026000293 --event evt-order-call-for-response-disposition --role predictor` — resolved paths.
- `uv run fedcourts query --help`
- `uv run fedcourts query --court scotus --disposition gvr --limit 5` — stderr: `ranged corpus reads: 32 GET(s), 8388608 byte(s)`. Returned five recent GVR rows (Casarez v. Irigoyen Farms; Huffman v. United States; Roybal v. Griffith; Harrington v. Martin; Cid v. United States); none related to this case, not used beyond confirming the shape.
- No CourtListener MCP calls and no web searches.
