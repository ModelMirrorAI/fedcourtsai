# Evaluator retrieval record

Read the provisioned event and outcome, all three candidates' blinded predictions, rationales, forecast documents, retrieval notes and harness-captured retrieval logs; the case-level context, document manifest, questions presented, relevant petition passages including Appendix A pages 1a-5a, and the November 9 docket snapshot. No new facts about this case were retrieved externally, and no opinion text, order or commentary was fetched.

## Historical aggregate context

To check base-rate use against the builds available to the candidates, ran the following commands with `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1 UV_OFFLINE=1`:

- `uv run fedcourts statpack-at data/cases/scotus/9026000436/record/blinded/gemini-baseline/ --ref origin/main --out-dir /tmp/statpack-at/gemini-baseline`
- `uv run fedcourts statpack-at data/cases/scotus/9026000436/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
- `uv run fedcourts statpack-at data/cases/scotus/9026000436/record/blinded/codex-baseline/ --ref origin/main --out-dir /tmp/statpack-at/codex-baseline`

Each selected build `0918fb18e74fb89adc9a0882411996400986925e`, digest `sha256:63295af7c6e50f69b51af1f372c8a86dd6e8a398f9e6bc408c56fd8af8ccaf4d`, and identified eligible alternative `1c4f550b7b758c0f5dbb4d505b8159cd8e93fee5` because the candidates recorded no build and checkout slack permits either. Inspected strictly prior-Term sal-v4 baseline-band records in both reconstructed builds, treating either as eligible evidence rather than comparing the candidates against today's version. These commands use statpack history only and emitted no ranged-corpus transfer line.

No evaluator `fedcourts query`, `open-events`, CourtListener MCP lookup or web search was made. Candidate-reported external retrieval was assessed from staged transcripts and was not repeated.
