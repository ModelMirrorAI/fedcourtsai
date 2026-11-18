# Retrieval Log

Beyond the provisioned case record (`event.yaml`, `outcome.json`, `record/context.json`, `record/snapshots/2026-11-16.json`, `record/documents/`, and `record/blinded/`) and the committed `metrics/statpack.md`:

1. **Candidate-time statpack reconstruction (`fedcourts statpack-at`):**
   - `uv run fedcourts statpack-at data/cases/scotus/9026000433/record/blinded/claude-baseline/ --ref origin/main --out-dir /home/runner/.gemini/tmp/fedcourtsai/statpack-at/claude-baseline`
   - Resolved candidate-time statpack build `7bcde3b105cb212283905eda17b827efc188e80c` (`sha256:84feb6798b6407fea2a17fed92c36d8a8db71d12850a967d840f018295ba4641`, `sal-v4`), shared by all three candidates (`run_id = 20261030T011325Z`).

2. **Corpus queries (`uv run fedcourts query` / `open-events`):**
   - None run.

3. **CourtListener MCP lookups:**
   - `mcp_courtlistener_search(type="o", citation="602 U.S. 899", fields=["caseName", "citation", "dateFiled"], num_results=2)` — attempted to cross-check a precedent citation (*Department of State v. Muñoz*, 602 U.S. 899 (2024)) in `gemini-baseline`'s forecast document; upstream CourtListener returned HTTP 504 Gateway Time-out.

4. **Web searches:**
   - None.
