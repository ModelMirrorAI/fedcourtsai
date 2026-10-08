# Retrieval — claude-judge, run 20261007T185906Z

Beyond the provisioned inputs (`event.yaml`, `outcome.json`, `record/context.json`,
`record/snapshots/2026-10-05.json`, `record/documents/*`, the three
`record/blinded/<alias>/` directories, the committed `metrics/statpack.md`, and the
repository docs and source read for the scoring rules):

- `uv run fedcourts segment-anchors --term 2026 --salience-version sal-v3` and the same
  command with `--salience-version sal-v4`. Both read only the committed
  `metrics/statpack.json` (no corpus; no `ranged corpus reads` line is printed by this
  command). Both printed the baseline band at risk_set 5.02% (n=12720), terminal 1.21%
  (n=9635), pooled over OT2017–OT2025. Used only to make the version-mismatch flag
  actionable; no rate was written into any `evaluation.json`.

No `fedcourts query` or `open-events` calls. No CourtListener MCP calls. No web searches.
