# Retrieval log

Beyond the provisioned inputs (`record/snapshots/2026-10-05.json`, `record/context.json`, `record/documents/{questions-presented,petition,brief-in-opposition}.txt`, `documents.json`), the event definition, and the committed `metrics/statpack.md`:

## Corpus

- `uv run fedcourts query --court scotus --disposition granted --era 2020s`
  stderr: `ranged corpus reads: 43 GET(s), 11075584 byte(s)`
  Returned eight modern granted priors (distribution counts 0–2, originating courts ca1/ca2/ca6/ca8/cadc or none). Used for shape only.

## CourtListener MCP

- `search` (type `o`, court `ca6`, filed after 2026-01-01): `Ream "Department of the Treasury" distilled spirits dwelling house` → 1 result: *John Ream v. U.S. Dep't of the Treasury*, No. 25-3259, filed 2026-04-21, published, panel Siler/Kethledge/Mathis.
- `search` (type `o`, court `ca5`, filed after 2026-01-01): `McNutt "Hobby Distillers" distilled spirits taxing power` → 1 result: *McNutt v. US Dept of Justice*, No. 24-10760, filed 2026-04-10, published.

## Web

- WebFetch `https://www.supremecourt.gov/RSS/Cases/JSON/26-93.json` (the companion *Ream* petition's docket). Read its proceedings: petition filed Jul 20 2026; federal respondents' brief Aug 14; eleven amicus entries Aug 19–20 (Ohio et al., Goldwater, CEI, NTUF, CIR, TPPF, PLF, Barnett, Cato, Manhattan Institute, Advancing American Freedom et al.); reply Sep 1; distributed for 9/28 conference Sep 2; rescheduled Sep 8; distributed for 10/9 conference Sep 23. No disposition. Nothing retrieved concerned this case's own disposition, which does not yet exist (conference is 10/9/2026).

Four retrieval calls in total.
