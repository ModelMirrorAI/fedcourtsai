# Retrieval beyond provisioned inputs

All successful CLI commands below used `UV_CACHE_DIR=/tmp/uv-cache UV_NO_SYNC=1` to use an allowed cache location without installing or synchronizing packages. No CourtListener MCP lookup was attempted. No search sought this petition's own disposition, and no other prediction or evaluation was read.

## Local contract, tooling, and base rates

- Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, and `schemas/agent_tooling.schema.json`; checked scoped instruction-file locations. Read the modern cert, circuit, paid relist/CVSG/amicus, and sal-v8 band sections of `metrics/statpack.md`. Used the frozen context anchor rather than current-Term rates.
- `uv run fedcourts paths --court scotus --docket 9026000332 --event evt-petition-disposition --role predictor`: first attempt failed before execution because the default uv cache was read-only. Repeated with the environment overrides above; resolved the case and event paths successfully. The tool did not expose an outcome path.
- `uv run fedcourts query --help`: read the structured-filter interface.

## Corpus lookups

1. `uv run fedcourts query --court scotus --disposition granted --era modern --limit 3`: refused because `modern` is not a valid decade token. No priors returned and no transfer line printed. Corrected the filter on the next call.
2. `uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026 --limit 3`: returned prior-Term grants in U.S. DOGE Service (25-1103), Corey Duran Berry (25-7026), and Blanche v. Ozurumba (25-1343). Their stored distribution counts were two, five, and two. This was a grant-selected orientation sample, not an estimate of grant likelihood or a substantive analogy. The Term mask selected prior docket Terms, not necessarily civil-calendar decision years.

   `ranged corpus reads: 33 GET(s), 8650752 byte(s)`

3. `uv run fedcourts query --court scotus --docket-number 26-199 --limit 1`: returned the Authority's related enforcement petition, pending, no recorded grant, zero recorded distributions. Output was reduced with `jq` to case and procedural fields. No opinion was requested.

   `ranged corpus reads: 14 GET(s), 3670016 byte(s)`

4. `uv run fedcourts query --court scotus --docket-number 26-201 --limit 1`: returned the FTC's related enforcement petition, likewise pending with no recorded grant and zero recorded distributions. Output was reduced with the same `jq` projection. These may be stale procedural fields, not proof of no scheduling.

   `ranged corpus reads: 0 GET(s), 0 byte(s)`

## Official-source web verification attempts

- Search query: `site.supremecourt.gov opinions 2024 FCC Consumers Research 720 appointments clause Gorsuch`. The web tool returned no usable response or sources. This searched for general precedent, not the present petition or its disposition.
- Open attempt: the Supreme Court's official slip-opinion PDF at path `/opinions/24pdf/24-354_0861.pdf`. Again, the web tool returned no usable content. No additional fact was learned. The account of Consumers' Research in the reasoning rests on the supplied petition and opposing briefs, not an independently retrieved opinion.

The provisioned 26-335 related snapshot was read as a supplied input. Its shared-amicus classification was distinguished from a formal Court cross-reference. No further live docket or outcome search was conducted.
