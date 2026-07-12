# Retrieval log — scotus/73272979 / evt-petition-disposition / claude-baseline / 20260712T114712Z

Beyond the provisioned inputs (snapshot, event definition, context.json):

1. **Committed statpack** — read `metrics/statpack.md`: the "Modern
   discretionary-cert petitions by disposition" section, the originating-circuit
   cuts, and the per-Term table (Term 2025: denied 92.6%, granted 4.9%,
   dismissed 2.5%) for base-rate context.
2. **Corpus priors** —
   `uv run fedcourts query --court scotus --era 2020s --limit 5 --corpus-backend ranged`
   - stderr: `ranged corpus reads: 402 GET(s), 105381888 byte(s)`
   - Returned five modern SCOTUS cert priors (counseled paid/IFP cert
     petitions); used only as weak context — none were original habeas
     petitions, so the statpack anchoring did the real work.

No CourtListener MCP calls, no REST fallback, and no web searches were made:
the provisioned snapshot already contained the docket's final order (see
`flags.json`), so outward retrieval about this case was neither needed nor
appropriate.
