# Evaluator Retrieval Log

1. **Path resolution (`fedcourts paths`):**
   - Command: `uv run fedcourts paths --court scotus --docket 73272491 --event evt-order-call-for-response-disposition --role evaluator`
   - Purpose: Resolve canonical case, event, outcome, and corpus paths.

2. **Prediction-time statpack reconstruction (`fedcourts statpack-at`):**
   - Command: `for alias in gemini-baseline claude-baseline codex-baseline; do uv run fedcourts statpack-at "data/cases/scotus/73272491/record/blinded/$alias/" --ref origin/main --out-dir "/tmp/statpack-at/$alias"; done`
   - Result: Reconstructed statpack build `7bcde3b105cb212283905eda17b827efc188e80c` (`digest`: `sha256:84feb6798b6407fea2a17fed92c36d8a8db71d12850a967d840f018295ba4641`), carrying `sal-v4`, into `/tmp/statpack-at/` to verify each candidate's base-rate citations against the pack in force at prediction run `20261029T142045Z`.

3. **Corpus query (`fedcourts query`):**
   - Command: `uv run fedcourts query --court scotus --docket-number 23-95 --limit 5`
   - Stderr: `ranged corpus reads: 21 GET(s), 5505024 byte(s)`
   - Purpose: Verify disposition (`denied` on `2023-12-11`) and `distribution_count` (`1`) of *Philip Esformes v. United States*, No. 23-95 (`scotus/72483418`), cited by candidates as a recent prior *Libretti* petition.

4. **CourtListener MCP / Web searches:**
   - None.
