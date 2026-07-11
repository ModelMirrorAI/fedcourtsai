"""Pipeline stages: ingestion (pull / live / historical), predict, evaluate.

The ingestion stages are deterministic (no agent needed) and run as scripts.
`predict` and `evaluate` are driven by coding agents via the prompt templates
in `.github/prompts/`; the helpers here just enforce the on-disk contract so
agent output is validated before it is committed.
"""
