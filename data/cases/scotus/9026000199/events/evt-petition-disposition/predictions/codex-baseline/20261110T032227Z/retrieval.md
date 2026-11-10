# Retrieval record

## Provisioned and local materials

Read `.github/prompts/predict.md`, `schemas/prediction.schema.json`, and `schemas/agent_tooling.schema.json`; the event definition; case-level `record/context.json`; `record/snapshots/2026-11-10.json`; `documents/documents.json`; the questions presented; selected substantive portions of the petition, all three combined responses, reply, and the available appellate opinion at the opening of the appendix. Read the related manifest and the three staged related docket snapshots, Nos. 26-201, 26-332, and 26-335. Consulted `metrics/statpack.md`, particularly the modern-cert, paid relist, CVSG, amicus, and sal-v8 reached-band sections. No outcome, other prediction, evaluation, or topic-label artifact was consulted.

## CLI calls and corpus queries

1. `uv run fedcourts paths --court scotus --docket 9026000199 --event evt-petition-disposition --role predictor` — initially failed because `/home/codexcell/.cache/uv/CACHEDIR.TAG` was on a read-only filesystem. No retrieval occurred.
2. `uv run fedcourts query --help` — initially failed for the same uv cache reason. No retrieval occurred.
3. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts paths --court scotus --docket 9026000199 --event evt-petition-disposition --role predictor` — succeeded and confirmed the case and event paths; the outcome path was not exposed or read.
4. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --help` — succeeded; read the structured-filter interface. No corpus transfer line.
5. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era modern --decided-before 2026-11-10 --limit 4` — rejected `modern` as an invalid era; returned valid decade tokens and flag guidance. No corpus transfer line.
6. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --disposition granted --era 2020s --decided-before 2026-11-10 --limit 4` — succeeded, returning four prior grants, a mixture of substantive applications and cert petitions. Visible examples included the Ruidosa Church application, Goldman Sachs Bank USA v. Brown (No. 25-1408, grant November 6, 2026, four distributions), and the New Hampshire election application. This was not a matched cert-only population and was not used to estimate a rate. Nothing returned was the target petition's disposition.

   `ranged corpus reads: 32 GET(s), 8388608 byte(s)`

7. `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts query --court scotus --docket-number 24-354 --decided-before 2026-11-10 --limit 1` — returned FCC v. Consumers' Research, case ID scotus/69797216: cert granted November 22, 2024, distribution count two, merits decided June 27, 2025, judgment reversed, no opinion body available. Used only as procedural context for the precedent already discussed in the provisioned record.

   `ranged corpus reads: 15 GET(s), 3932160 byte(s)`

Both successful corpus queries reported the date cutoff of November 10, 2026. This cell itself is forward, not replay. Neither query requested `--full`.

## CourtListener MCP

- `search(type="o", court="ca6", citation="163 F.4th 294", num_results=3)` — query ID `7e180f61`, count zero, no results. Did not interpret the empty result as disproving the opinion; relied on its treatment in the provisioned filings. No REST fallback attempted.

## Web attempts

- `web.run` search for `site.supremecourt.gov opinions 2024 FCC Consumers Research 24-354 June 27 2025 private delegation` — no usable result content was returned.
- `web.run` open of the general-precedent PDF candidate `https://www.supremecourt.gov/opinions/24pdf/24-354_0861.pdf` — no usable content was returned. Its filename was not treated as verified and no proposition was drawn from it.

These attempts concerned the general Consumers' Research precedent, not the present petition's outcome or subsequent history. No live search for this case's disposition was made.

## Validation

The cell validation command is `UV_CACHE_DIR=/tmp/uv-cache uv run fedcourts validate data --cell data/cases/scotus/9026000199/events/evt-petition-disposition/predictions/codex-baseline/20261110T032227Z`. It checks output completeness and schemas, not additional case evidence.
