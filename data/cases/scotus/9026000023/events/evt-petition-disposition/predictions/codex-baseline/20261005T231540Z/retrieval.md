# Retrieval record

## Provisioned evidence

Read the case-level snapshot `record/snapshots/2026-10-05.json`, `record/context.json`, the event definition, and `record/documents/documents.json`, `questions-presented.txt`, and relevant petition sections and lower-court appendix. No outcome file or other predictor's output was read.

## Local context beyond the provisioned inputs

- Read `AGENTS.md`, `.github/prompts/predict.md`, and the prediction, tooling-feedback, and flags schemas for the output contract.
- Read the committed `metrics/statpack.md` modern-cert disposition, circuit, paid relist/CVSG, and sal-v4 Term/band sections. Read `metrics/statpack.json` aggregate metadata and prior-Term baseline risk-set fields. Pooled all displayed OT2017–OT2025 baseline reached rows: 638 grant-family cases divided by a weighted denominator of 12,720, or 0.05015723270440252. No individual historical case rows were queried.
- Ran `uv run fedcourts paths --court scotus --docket 9026000023 --event evt-petition-disposition --role predictor`. The first attempt failed because the default uv cache was read-only; rerunning with a temporary cache succeeded. This resolves paths and is not a corpus query.
- No `fedcourts query`, `open-events`, corpus pull, or CourtListener MCP lookup was used. Consequently there are no ranged-corpus-read transfer lines to report.

## Web retrieval: general pre-existing doctrine only

1. Search: `site.supremecourt.gov opinions 2013 Sprint Communications Jacobs 12-815 Younger`. This sought the older general abstention precedent, not this petition. The results included a Cornell copy of Sprint and an unrelated official Rogers v. Drew opinion result. The Rogers result was not opened or used.
2. Search: `Harper Public Service Commission 396 F.3d 348 2005 opinion`. This sought the older comparator cited in the provisioned petition. Results included the Justia opinion copy and CourtListener; a companion-case result also appeared with a snippet quoting Harper. I did not open that companion result or use it to update companion posture, and it did not disclose a Supreme Court disposition in the surfaced snippet.
3. Opened the Harper opinion copy: `https://law.justia.com/cases/federal/appellate-courts/F3/396/348/592451/`. Used its treatment of generalized state interests, interstate commerce, and the caution against treating any Commerce Clause allegation as automatically defeating abstention.
4. Opened the Sprint opinion copy: `https://www.law.cornell.edu/supremecourt/text/12-815`. Used the narrow exceptional-category framework and its treatment of civil enforcement proceedings.
5. Searched within that Sprint page for `exceptional` to verify the doctrinal language. No case-specific docket retrieval occurred.

These authorities are cited by case name, reporter, and pinpoint in `reasoning.md`. Neither legal source supplies this petition's outcome. No Supreme Court disposition of the target petition was sought, encountered, or incorporated. The companion posture used in the forecast comes solely from the supplied petition.
