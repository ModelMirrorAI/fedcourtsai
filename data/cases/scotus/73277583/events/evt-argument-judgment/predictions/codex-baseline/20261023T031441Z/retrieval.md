# Retrieval beyond the provisioned case inputs

No lookup sought Beaird's disposition, subsequent history, or decision coverage. The forward-mode forecast rests on the frozen record and pre-decision briefing and argument. No other cell's prediction or evaluation was read.

## Committed general context

- Read the merits section and header of `metrics/statpack.md`; inspected the top-level metadata keys of `metrics/statpack.json` for freshness information. A local Python calculation pooled only published grant-Term rows in 2015–2024: 360 disturbed, 516 parsed, 539 included grants, and 56 exclusions outside that cohort. No corpus query or open-events lookup was run, so there is no ranged-corpus transfer line.
- Read the prediction, flags, and tooling schemas and the cell contract. `fedcourts paths --court scotus --docket 73277583 --event evt-argument-judgment --role predictor` resolved the input paths; the initial invocation failed because the default uv cache was read-only, and the same invocation succeeded with `UV_CACHE_DIR=/tmp/uv-cache`.

## Web retrieval of historical authorities

1. Search: `site.supremecourt.gov opinions Kisor Wilkie 2019 Stinson sentencing guidelines genuine ambiguity`.
2. Search in the same call: `site.supremecourt.gov opinions 2024 Loper Bright footnote 5 express delegation`.
3. Opened the Court's Kisor slip opinion, official document path `supremecourt.gov/opinions/18pdf/18-15_9p6b.pdf`, for its genuine-ambiguity and regulatory-deference framework. The opinion is dated June 26, 2019.
4. Search: `site.supremecourt.gov/opinions/23pdf "Loper Bright" "22-451"`.
5. Opened the Court's Loper Bright slip opinion, official document path `supremecourt.gov/opinions/23pdf/22-451_7m58.pdf`; searched within it for `as defined by` to verify footnote 5's express-delegation examples. The opinion is dated June 28, 2024.

Search results incidentally included a May 2026 entry discussing the Stinson question in this case. It was not opened, supplied no observed judgment, and was not used as case evidence. Only the historical judicial opinions were used from web retrieval.

## CourtListener MCP

1. Opinion search with `citation="508 U.S. 36"`, requesting one result. It returned the unrelated Morley v. Central Intelligence Agency, 508 F.3d 1108 (2007), rather than Stinson; that result was disregarded.
2. Opinion search restricted to the Supreme Court, case name `Stinson v. United States`, and filing dates in 1993. It returned Stinson, 508 U.S. 36 (May 3, 1993), opinion ID `112854`.
3. Read opinion `112854` for Stinson's holding, its limits, and the relationship between Guidelines commentary, policy statements, and the Seminole Rock analogy. This is the historical Stinson case, not this cell's outcome.

No direct CourtListener REST request was made, and no credentials were accessed.
