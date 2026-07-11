# Retrieval Log

**Case:** Zhang v. Federal Home Loan Bank of Topeka  
**Docket No.:** 10th Cir. No. 24-3029 (D.C. No. 5:19-CV-04073-TC, D. Kan.)  
**Event ID:** `evt-appeal-disposition`  
**Predictor ID:** `gemini-baseline`  
**Run ID:** `20260711T043934Z`  
**Model ID:** `gemini-3.5-flash`

---

## 1. CourtListener MCP Lookups
The following retrievals were executed using the CourtListener MCP server:
*   `mcp_courtlistener_get_endpoint_item(endpoint_id="dockets", item_id=69641076)` — Fetched the docket details for Tenth Circuit Docket No. 24-3029. This confirmed the docket information, case name, and linked opinion cluster URL.
*   `mcp_courtlistener_get_endpoint_item(endpoint_id="clusters", item_id=10333578)` — Fetched the opinion cluster `10333578`, which was found under `clusters` in the docket. This provided the date filed (`2025-02-14`), the sub-opinion URL, and general metadata.
*   `mcp_courtlistener_get_endpoint_item(endpoint_id="opinions", item_id=10800166)` — Fetched the sub-opinion details, including the full plain text of the order and judgment. This was the decisive resource for our qualitative analysis and prediction.

---

## 2. Local File / Committed Context Lookups
*   Read `metrics/statpack.md` (committed on git) to check the base rates of resolved cases in the Tenth Circuit (ca10).
*   Read `schemas/prediction.schema.json` to verify schema conformance.
*   Read `schemas/agent_tooling.schema.json` to verify schema conformance.
*   Read `schemas/agent_flags.schema.json` to verify schema conformance.

---

## 3. Remote Corpus Queries
*   `uv run fedcourts corpus-info --corpus-backend ranged` was executed but failed because the `DVC_REMOTE_URL` was not set in the local environment variables. No remote corpus queries were made.
