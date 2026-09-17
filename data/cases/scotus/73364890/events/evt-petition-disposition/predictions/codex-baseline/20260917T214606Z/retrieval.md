# Retrieval record

## Local sources beyond the provisioned case

- Read the governing `AGENTS.md`, `.github/prompts/predict.md`, prediction schema, flags schema, and tooling schema. Read relevant path, ID, and serialization helpers solely to place and validate the output.
- Read `metrics/statpack.md`: modern discretionary-cert dispositions, originating-circuit cut, paid-segment relist/CVSG cuts, and sal-v4 segment table. Read corresponding aggregate fields in `metrics/statpack.json`. Pooled only rendered Terms 2017–2024 for the numerical anchor: 593 / 11,580. Inspected the pack's last-change commit date with `git log -1 --format='%h %cI' -- metrics/statpack.json`.
- Ran `uv run fedcourts paths --court scotus --docket 73364890 --event evt-petition-disposition --role predictor`. The first invocation failed because the default uv cache was read-only; retrying with a cache under `/tmp` succeeded. This resolves paths and retrieves no case outcome.
- No `fedcourts query`, `open-events`, corpus pull, or live CourtListener MCP lookup was made. Consequently there are no ranged-corpus transfer lines to report. No per-case historical prior was retrieved.

## External attempts

All external attempts concerned general procedural rules, not this case, its island, its parties, its current docket, or its outcome. The web tool returned no usable source content or citations for the following searches and opens. Repeated attempts are retained here rather than represented as successful consultation.

Search batches, in order:

1. `site.uscourts.gov Federal Rules Civil Procedure Rule 52 findings oral documentary evidence clearly erroneous 1985 amendment`; `site.supremecourt.gov Rule 10 writ certiorari rarely granted erroneous factual findings misapplication properly stated rule`.
2. `site.uscourts.gov "Rule 52" "oral or other evidence"`; `site.supremecourt.gov "Rule 10" "erroneous factual findings"`.
3. `site.uscourts.gov "2025" "civil" "52" "documentary" rules`; `site.uscourts.gov "Rule 52" "1985 Amendment"`.
4. `site.uscode.house.gov "Rule 52" "Findings of fact, whether based on oral or other evidence"`; `site.uscode.house.gov "Rule 52" "The principal argument advanced"`.
5. `Federal Rule Civil Procedure 52 oral documentary evidence 1985 amendment`.
6. `site.uscourts.gov "2025" "federal-rules-of-civil-procedure"`; `site.supremecourt.gov "2026" "Rules of this Court" "February"`.

Web page opens and the final in-page search targeted these general official resources, with repeats where earlier attempts supplied nothing:

- The House U.S. Code Rule 52 page, twice: `https://uscode.house.gov/view.xhtml?edition=prelim&num=0&req=granuleid%3AUSC-prelim-title28a-node89-node145-rule52`.
- The Court's rules guidance page, four times: `https://www.supremecourt.gov/filingandrules/rules_guidance.aspx`.
- The judiciary's civil-rules landing page, twice: `https://www.uscourts.gov/forms-rules/current-rules-practice-procedure/federal-rules-civil-procedure`.
- `https://www.supremecourt.gov/filingandrules/2023RulesoftheCourt.pdf`.
- `https://www.govinfo.gov/content/pkg/USCODE-2023-title28/pdf/USCODE-2023-title28-app-federalru-dup1.pdf`.
- An in-page search for `erroneous factual` at `https://www.supremecourt.gov/filingandrules/2026RulesoftheCourt_WEB.pdf`.

Shell fallbacks used no CourtListener endpoint or credentials:

- Attempted `curl` of `https://www.uscourts.gov/sites/default/files/2025-12/federal-rules-of-civil-procedure-december-1-2025.pdf` into `pdftotext`; the URL returned 404 and `pdftotext` was unavailable.
- Attempted `curl` of the Court's 2026 rules PDF into `pdftotext`; the extractor was unavailable and curl reported a failed write. No rule text was extracted.
- Attempted a Python standard-library HTTP read of `https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title28a-node89-node145-rule52&num=0&edition=prelim`, looking only for Rule 52 text and the 1985 amendment note; it timed out.

No external source content informed the forecast. The legal analysis rests on the supplied petition and appended lower-court opinion; the numerical prior rests on the committed aggregate statpack.
