# Bryan v. United States — evt-petition-disposition

**Prediction: not granted (granted = 0), P(granted) = 0.06, predicted
disposition `other`, confidence 0.65.**

## What the snapshot contains

The 2026-07-04 snapshot is a sparse bulk-import CourtListener docket (source
16, created 2014, no PACER lineage): case name *Bryan v. United States*, court
`scotus`, one associated opinion cluster (cluster 87450), and **no docket
entries, no filing/argument/decision dates, no docket number, and no petition
documents**. The only case-specific facts available are the caption, the court,
and the existence of a decided opinion cluster.

## What the case is

The caption matches more than one historical Supreme Court merits case, and the
snapshot carries nothing (no docket number, no dates) to disambiguate. The two
leading candidates — this identification is background legal knowledge, the
kind of precedent context the contract permits, not a new docket fetch — are:

- *Bryan v. United States*, 338 U.S. 552 (1950): certiorari to the Fifth
  Circuit on whether an appellate court that reverses for insufficiency of the
  evidence may remand for a new trial rather than direct acquittal. Certiorari
  was granted; the Court **affirmed** the judgment below, and Bryan lost.
- *Bryan v. United States*, 524 U.S. 184 (1998): certiorari to the Eleventh
  Circuit on the mens rea for "willfully" dealing in firearms without a license
  under 18 U.S.C. § 924(a)(1)(D). Certiorari was granted; the Court (Stevens,
  J.) **affirmed** the conviction, and Bryan lost.

Either way the shape is the same: a certiorari case that reached a merits
opinion in which the petitioner's judgment below was affirmed. The docket's
opinion cluster confirms a decided merits opinion exists, which is consistent
with both candidates and with nothing else in the snapshot.

## Legal question and governing standard

The event asks for the disposition of the petition
(granted/denied/granted-in-part/dismissed/withdrawn/other). For a historical
merits case the operative question is not the modern cert-stage forecast (the
petition was in fact granted long ago — that is why an opinion cluster exists)
but how the pipeline's reconciler labels a decided merits case whose judgment
was an **affirmance against the petitioner**.

## Mapping to the event's disposition labels

Corpus base rates (`fedcourts stats --court scotus --resolved-only`, 296
resolved events) show how the pipeline actually labels this population of
sparse opinion-import SCOTUS dockets: **`other` 78.4%, `dismissed` 15.9%,
`denied` 4.4%, `granted` 1.4%**. Merits affirmances/reversals have no direct
label in the enum and overwhelmingly reconcile to `other`. A `fedcourts query
--disposition granted` spot-check shows the rare `granted` labels attach to
cases whose opinions themselves grant something (e.g. an original-jurisdiction
writ), not to ordinary certiorari merits cases.

## Calibration

- `granted = 0`, `probability = 0.06`: the corpus-wide grant share is 1.4%. I
  set P(granted) somewhat above that base rate because, unlike a writ-of-error
  case, certiorari here *was* historically granted, and both candidate opinions
  contain grant-of-certiorari language a text-driven reconciler could latch
  onto. The empirical labeling says it usually does not, so the probability
  stays low.
- `predicted_disposition = other` rather than `denied`: the legal outcome
  (petitioner loses, judgment affirmed) is not in real doubt for either
  candidate identification; the choice of `other` follows the pipeline's
  realized labeling convention (78.4% `other`), with `dismissed`/`denied` the
  main alternative mappings. Confidence 0.65 reflects that label-mapping risk
  plus the residual ambiguity about which *Bryan* this docket is.
- **No per-judge votes.** With the docket unidentifiable between at least two
  candidate cases decided by different Courts (the Vinson Court in 1950, the
  Rehnquist Court in 1998), per-justice votes would be speculation; I omit
  them.
