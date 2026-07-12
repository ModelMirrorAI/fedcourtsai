# In Re Deryl Nelson, No. 25-5077 (scotus/73272979) — evt-petition-disposition

## Threshold disclosure: the provisioned snapshot already contains the disposition

This cell is marked `forward` (`record/context.json`), but the provisioned
baseline snapshot (`record/snapshots/2026-07-12.json`) records the final order
on its face. The Oct 20 2025 docket entry reads:

> The motion for leave to proceed in forma pauperis is denied, and the petition
> for a writ of habeas corpus is dismissed. See Rule 39.8. As the petitioner has
> repeatedly abused this Court's process, the Clerk is directed not to accept
> any further petitions in noncriminal matters from petitioner unless the
> docketing fee required by Rule 38(a) is paid and the petition is submitted in
> compliance with Rule 33.1. See Martin v. District of Columbia Court of
> Appeals, 506 U. S. 1 (1992) (per curiam).

I did not retrieve this; it arrived in the guaranteed-common baseline input. Per
the contract I disclose it here and in `flags.json` so the evaluation can
discount the cell — this is not a genuine forward prediction. The event file
(`event.yaml`) still shows `resolved: false`, which looks like a pipeline lag
between the refreshed snapshot and event resolution.

## The prediction, reasoned as if the order were absent

Even setting the Oct 20 entry aside, every pre-decision feature of this record
points the same way:

- **Legal posture.** This is an *original* petition for a writ of habeas corpus
  filed directly in the Supreme Court (an "In Re" 25-5xxx docket), not a cert
  petition seeking review of a lower-court judgment (`LowerCourt` is null).
  Under Sup. Ct. R. 20.4(a), an original habeas writ issues only in
  "exceptional circumstances" where "adequate relief cannot be obtained in any
  other form or from any other court." The Court has not granted such a
  petition in decades; the realistic outcomes are denial or Rule 39.8
  dismissal, and grant probability is effectively zero.
- **Petitioner profile.** A pro se state prisoner (Muskegon Correctional
  Facility, MI, prisoner #348736) proceeding in forma pauperis, self-
  represented (`sJsonCaseType: IFP`). IFP petitions succeed far more rarely
  than paid ones even in the cert population; pro se original habeas petitions
  essentially never succeed.
- **Docket signals.** No response was requested, no CVSG, no amicus activity.
  The petition was distributed for conference three times (9/29, 10/10,
  10/17 2025) with one reschedule — but repeated distribution of an IFP
  original petition is far more consistent with the Court preparing a Rule
  39.8 sanction (which requires noting the petitioner's abuse history) than
  with grant interest. The invocation of *Martin v. District of Columbia Court
  of Appeals* confirms petitioner is a repeat abusive filer, i.e. this was not
  his first frivolous filing.
- **Base rates.** The committed statpack's modern discretionary-cert section
  (Term 2025 row: denied 92.6%, granted 4.9%, dismissed 2.5%; grant rate 4.9%)
  is the population *ceiling* — it describes counseled paid and IFP cert
  petitions. An IFP original habeas petition from a repeat filer sits at the
  extreme unfavorable tail of that distribution. Corpus priors retrieved via
  `fedcourts query` (2020s SCOTUS slice) were counseled cert petitions and
  serve only to confirm that grants cluster among paid, counseled petitions
  with substantial distribution/relist activity of a different character.

## Conclusion

Predicted disposition: **dismissed** (IFP denied, petition dismissed under Rule
39.8), which is what the record shows and what the pre-decision signals
independently compel. `granted = 0`, `probability` (P(granted)) = 0.001 — I
leave a sliver rather than 0.0 only as calibration hygiene; conditional on this
record the grant outcome is not a live possibility. Confidence 0.98. No
per-justice votes are predicted: Rule 39.8 dispositions issue per curiam
without recorded votes.
