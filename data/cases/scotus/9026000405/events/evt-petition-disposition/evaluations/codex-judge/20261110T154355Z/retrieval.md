# Evaluator retrieval record

Read only the evaluation contract and schemas, this cell's provisioned event/outcome, context, docket snapshot, petition and questions-presented texts, and the three blinded candidates' prediction, rationale, forecast, retrieval note and captured retrieval log. No corpus query, open-events call, CourtListener MCP lookup or web search was made by this evaluator. No case opinion or order was retrieved externally.

## Historical statistical context

- Command: `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts statpack-at data/cases/scotus/9026000405/record/blinded/claude-baseline/ --ref origin/main --out-dir /tmp/statpack-at/claude-baseline`
- Succeeded: build `dedb32b153e67d254af10083c3ee247cecd56116`, landed `2026-10-31T10:28:26-04:00`, digest `sha256:a059cb872f890b63515d8e2ac6ef798347ae7231a62d08543a5b7431bd941faa`, with no alternative build. The recorded digest came from `cert_anchor`.
- All three masked predictions record this same digest and prediction run. Used the recovered `statpack.md` to check their descriptions of historical marginal cuts and reached-versus-terminal populations. No independent scored baseline was pooled or quoted.
- This is statpack-history reconstruction, not a corpus lookup; it prints no `ranged corpus reads` line. No prediction history or identity-resolution material was consulted.

## Validation

Validated all three written evaluation objects against `schemas/evaluation.schema.json` with the available system Python `jsonschema` package and date-time format checking, and validated the tooling report against `schemas/agent_tooling.schema.json`. Independently checked each score against its masked prediction and outcome, alias/path consistency, omitted harness-owned fields, and the exact eight-file output set. All checks passed. No package installation or whole-tree validation was performed. The project virtual environment does not include `jsonschema`, but the system interpreter already does.
