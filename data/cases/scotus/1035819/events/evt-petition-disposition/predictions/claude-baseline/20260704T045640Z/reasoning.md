# Mitchell v. Board of Comm'rs of Leavenworth Cty. — petition disposition (scotus/1035819)

## The question

Will this Supreme Court petition be granted? The event is
`evt-petition-disposition` with `decision_target: disposition`, so the call is
the realized disposition label the pipeline will record for this case.

## What the snapshot shows

The snapshot (`data/cases/scotus/1035819/record/snapshots/2026-07-04.json`) is
metadata-only, but two structural facts carry the prediction:

- **A linked published opinion cluster** (`clusters` holds one CourtListener
  cluster URL). The docket was created in 2014 with `source: 16` — a record
  digitized from published reports, not a tracked live docket. A case with a
  published Supreme Court opinion was decided **on the merits**; it is not a
  pending discretionary cert petition awaiting a grant/deny.
- **An empty docket number** and every activity date null (`date_filed`,
  `date_cert_granted`, `date_cert_denied`, `date_terminated`), with no docket
  entries, parties, or counsel. The outcome is not leaked; the event is open as
  presented, but only because the record is sparse, not because the case is
  live.
- **Caption `Mitchell v. Board of Comm'rs of Leavenworth Cty.`** — an
  individual against a Kansas county's board of commissioners, a posture
  consistent with a 19th-century civil dispute reaching the Court under the
  pre-1925 mandatory appellate jurisdiction (writ of error), where review was
  as of right and the recorded disposition is a merits label (affirmed /
  reversed / dismissed), not a cert grant or denial.

## Governing framework

For a modern petition the governing standard would be Sup. Ct. R. 10
(discretionary certiorari, a low single-digit grant rate). But everything
structural about this record says pre-discretionary era: digitized from
reports, published opinion attached, no Term-year docket number. In that
regime "granted" in the modern cert sense is not the outcome the record will
ever show; the disposition that gets recorded for such cases in this corpus is
the merits label, which the schema's enum captures as `other` (or `dismissed`
for the era's frequent dismissals for want of jurisdiction).

## Base rates

`fedcourts stats --court scotus --resolved-only` over the corpus's 296
resolved SCOTUS events: **other 78.4%**, dismissed 15.9%, denied 4.4%,
**granted 1.4%**. The resolved set is dominated by exactly this class —
digitized historical dockets whose disposition came from the linked opinion —
so it is the right reference class for this case, and it points strongly to
`other`. `fedcourts query --court scotus` confirms the resolved priors are
old, sparse, cluster-backed records labeled overwhelmingly `other`.

## Weighing

Conditional on a published opinion existing, the mass concentrates further on
the merits labels: `other` first, `dismissed` (want of jurisdiction) second.
`granted`/`denied` in the cert sense are near-floor — the corpus records them
for only ~6% of resolved SCOTUS events combined, and those skew toward
genuinely cert-era dockets, which this is not. I keep a little probability on
`granted` because the outcome-labeling path for this row is itself uncertain
(see caveats).

**Prediction: `other`.** P(granted) = **0.02**, `granted = 0`, confidence 0.6.
The confidence reflects label-mapping uncertainty between `other` and
`dismissed`, not doubt that the case was long ago decided on the merits. No
per-judge votes: the snapshot carries no panel or Term-composition
information, so nine named votes would be invention rather than inference.

## Caveats — why this case is in scope at all

This case appears to be exactly the class the predict scope excludes as
"published opinion but no machine-readable cert disposition" (issue #363 —
`is_published_opinion_unresolvable`): still open, SCOTUS, outcome living only
in an opinion. It reached the predict matrix anyway because the exclusion
tests the **corpus row's** `citations` / `citation_count` / `opinion_text`,
and this row has all three empty — the cluster link visible in the docket
snapshot never populated the row's citation fields. The empty docket number
likewise defeats the pre-1925 (`#309`) and stale-Term (`#333`) predicates,
which need a parseable number. So the case is in scope through an ingestion
gap, not by design; flagged in `flags.json` (scope + data-quality) so the
recoverability probe / cluster backfill can pick it up.
