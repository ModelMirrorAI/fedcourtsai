# Retrieval log

## Provisioned inputs

Read the cell's event.yaml, record/context.json, record/snapshots/2026-10-04.json, and record/documents/{documents.json,questions-presented.txt,petition.txt,brief-in-opposition.txt}. Relied on the questions presented and the briefs' issue, vehicle, and preservation discussions. No appendix text was provisioned or retrieved.

## Additional local context

- Read metrics/statpack.md: modern discretionary-cert dispositions; originating-circuit, paid relist-count and CVSG cuts; and the sal-v4 prior-Term reached-band table.
- Read metrics/statpack.json to pool the baseline band's prefix_est_grant_rate weighted by prefix_weighted_resolved across displayed Terms 2017-2025: 638 / 12,720 = 0.05015723270440252.
- Ran `git log -1 --format='%h %cI' -- metrics/statpack.json` to distinguish pack commit vintage from live corpus freshness. Result: September 28, 2026 at 12:02:50 UTC. This is not a corpus-pull timestamp.
- Read the task contract, repository instructions, output schemas, and path/serialization helper definitions solely for artifact construction. Ran `fedcourts paths --court scotus --docket 9026000027 --event evt-petition-disposition --role predictor`; the first uv invocation failed on a read-only default cache, and the retry with a writable temporary cache succeeded.

## External general-law attempts

1. Web search: `site.supremecourt.gov "Rule 10" "misapplication of a properly stated rule of law"`. No usable search text returned.
2. Web open: `https://www.supremecourt.gov/filingandrules/2023RulesoftheCourt.pdf`. No usable text returned.
3. Web open: `https://www.supremecourt.gov/filingandrules/rules_guidance.aspx`. No usable text returned.
4. Shell attempt: `curl -fsSL --max-time 30 https://www.supremecourt.gov/filingandrules/2023RulesoftheCourt.pdf | pdftotext - - | sed -n '/Rule 10. Considerations Governing Review/,/Rule 11. Certiorari/p' | head -65`. The extraction failed because pdftotext is not installed; curl reported a downstream write failure. No rules text was read or used from this attempt.

No case-specific web searches, live CourtListener calls, `fedcourts query`, or `fedcourts open-events` calls were made. There are no ranged-corpus transfer lines to report. The external attempts contributed no evidence and exposed no outcome information.
