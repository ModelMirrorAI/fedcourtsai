# Retrieval log

## Provisioned materials

- Read the event definition, context, October 3, 2026 snapshot, document manifest, questions presented, and selected substantive portions of the petition and brief in opposition.
- Did not inspect outcomes, other predictors' outputs, or topic-label artifacts.

## Beyond the provisioned record

- Read `metrics/statpack.md`: modern-cert disposition population, paid-segment relist and CVSG cuts, and sal-v4 reached-band table. Read `metrics/statpack.json` for exact prior-Term elevated-band numerators and denominators. Pooled Terms 2017–2024 only: 484 / 2810 = 0.1722419929. No live corpus query or ranged-read transfer line was generated.
- Web search: `site.supremecourt.gov opinions Barnes Felix 2025 totality circumstances qualified immunity`. No usable results returned.
- Web open attempted the official Barnes slip opinion at `https://www.supremecourt.gov/opinions/24pdf/23-1239_onjq.pdf`. No usable content returned.
- CourtListener MCP `search`: type `o`, case name `Barnes v. Felix`, court `scotus`, filed before `2025-06-01`, maximum three results. Returned two records of the May 15, 2025 Supreme Court opinion, not the target petition's outcome.
- CourtListener MCP `read_document`: opinion 11051434, chunks 0 and 1, chunk size 9000. Read the background and framing of the temporal-cutoff issue; the tool response was partly truncated.
- CourtListener MCP `search_document`: opinion 11051434, literal query `no time limit`, context 1600 characters. Read the majority's discussion of earlier circumstances and the instant of force, slip opinion pp. 5–6.

## Local contract and tooling

Read AGENTS.md, the prediction prompt, prediction/flags/tooling schemas, and the serialization helper. Used `fedcourts paths --court scotus --docket 73527306 --event evt-petition-disposition --role predictor`. The first uv invocation encountered a read-only default cache; using a cache under `/tmp` succeeded. Arithmetic used jq over the committed aggregate. Validation is a local artifact check, not retrieval of a disposition.
