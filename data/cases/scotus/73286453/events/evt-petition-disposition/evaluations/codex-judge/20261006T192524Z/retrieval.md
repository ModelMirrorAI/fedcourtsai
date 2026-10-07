# Evaluator retrieval

No external retrieval. No corpus query or open-events lookup, CourtListener MCP lookup, or web search was performed by this evaluator.

Read the provisioned event, outcome, case context, blinded prediction/prose/retrieval artifacts for gemini-baseline, claude-baseline, and codex-baseline, the document manifest and questions presented, selected petition and opposition passages, and the October 5, 2026 docket snapshot. Candidate retrievals described in the evaluations are observations from their staged logs, not evaluator retrievals.

Read the committed `metrics/statpack.md`, especially the sal-v4 band table. Locally calculated the denominator-weighted baseline reached rate over Terms 2017–2024, excluding the predictions' own Term 2025 and the later 2026 row. All 10 pack Terms are rendered. Weighted denominator: 11,580; pooled rate from rounded percentages: 0.05120250431778929. No remote corpus freshness claim is made.

Operational reads covered AGENTS.md, the evaluation prompt, output schemas, and path/serialization helpers. Output validation is local and alias-keyed; full-tree validation is left to the post-run harness after restoration and un-aliasing.
