# Retrieval record

## Provisioned inputs

Read the event definition, the case-level snapshot `2026-11-09.json`, context, document manifest, questions presented, lower-court docket summary, and relevant sections of every provisioned filed-document text: petition, combined BIO, cert reply, invited SG brief, combined supplemental briefs, and decision below. No other prediction, evaluation, outcome file, or topic-label artifact was read. No retrieval of this case's own live disposition or subsequent history was attempted.

## Corpus and committed base rates

- Consulted `metrics/statpack.md`, especially the relist-count, CVSG, and sal-v8 reached-band tables, and selected structure/counts in `metrics/statpack.json`. A `jq` aggregation of relist buckets 1 and above returned 726 grants/GVRs over 3,510 resolved petitions. Used the provisioned frozen cert anchor as the primary calibration reference.
- Attempted `uv run fedcourts paths --court scotus --docket 73279966 --event evt-order-relist-disposition --role predictor`. It failed before execution because uv's default cache was read-only. Repeated successfully as `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts paths --court scotus --docket 73279966 --event evt-order-relist-disposition --role predictor`. This resolved paths, not outcome information.
- Read CLI help using `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --help`; repeated with a wider `COLUMNS` setting and a bounded display to read the flags. No corpus lookup occurred in the help calls.
- Attempted `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --era modern --disposition granted --decided-before 2025 --limit 5`. Rejected: era must be a decade token, not `modern`. No read-statistics line or corpus rows were returned.
- Corrected to `UV_CACHE_DIR=/tmp/uv-cache uv run --no-sync fedcourts query --court scotus --era 2020s --disposition granted --decided-before 2025 --limit 5`.
  Transfer report: `ranged corpus reads: 80 GET(s), 20905984 byte(s)`.
  Returned RiseandShine v. PepsiCo (24-1016), Monsanto v. Durnell (24-1068), Hikma v. Amarin (24-889), Cisco v. Doe I (24-856), and Pitchford v. Cain (24-7351). The first four show CVSG dates and three distributions; Pitchford shows eight distributions without a CVSG. These were selected grant examples, not a denominator or an estimate of grant likelihood. The Term filter uses derived year, so returned grant dates can fall in 2026; these all precede this forward forecast date. No opinion bodies were requested.

## CourtListener MCP

- `search(type="o", citation="596 U.S. 832", num_results=3)`: returned United States v. Washington, decided June 21, 2022, opinion 6351405, cluster 6479294, plus an irrelevant Federal Circuit citation-number match that I disregarded. The former supplied the official opinion filename and historical case metadata.
- `search_document(opinion_id=6351405, query="discriminat", snippet_size=600)`: returned 20 of 33 matches, including the intergovernmental-immunity nondiscrimination rule and the holding concerning Washington's Hanford workers' compensation law. Used only as limited doctrinal background; not a lookup of this petition or its outcome.

## Web attempts

- Search: `site.supremecourt.gov opinions "United States v. Washington" "596" "2022"`. The web tool returned no usable result content.
- Search: `"21-404" "2022" "opinion"`. The web tool again returned no usable result content.
- Open, using the official filename supplied by CourtListener: `https://www.supremecourt.gov/opinions/21pdf/21-404_i5ea.pdf`. No usable content was returned. No claim in the prediction rests on a web result.

These attempts concerned a 2022 precedent, not the pending petition. None surfaced an outcome for this case. All uv commands after the initial failure used a temporary writable cache and `--no-sync`; nothing was installed. Operational schema inspection and cell validation are not additional substantive retrieval.
