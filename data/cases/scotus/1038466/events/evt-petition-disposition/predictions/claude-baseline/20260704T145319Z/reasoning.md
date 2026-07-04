# Mason v. Rollins — evt-petition-disposition

**Prediction: not granted (granted = 0), P(granted) = 0.03, predicted
disposition `other`, confidence 0.6.**

## What the snapshot contains

The 2026-07-04 snapshot is a sparse bulk-import CourtListener docket (source
16, created 2014, no PACER lineage): case name *Mason v. Rollins*, court
`scotus`, one associated opinion cluster (cluster 88494), and **no docket
entries, no filing/argument/decision dates, no docket number, no
originating-court information, and no petition documents**. The only
case-specific facts available are the caption, the court, and the existence of
a decided opinion cluster.

## What the case is

The caption and the low CourtListener cluster id (88494, a range populated by
nineteenth-century U.S. Reports opinions) point to the historical Supreme Court
case *Mason v. Rollins*, 80 U.S. (13 Wall.) 602 (1871) — this identification is
background legal knowledge, the kind of context the contract permits, not a new
docket fetch. That case reached the Court from the Circuit Court for the
Northern District of Illinois in litigation involving a federal internal
revenue collector (a companion circuit-court decision by Chase, Circuit
Justice, is reported at 16 F. Cas. 1061). I do not confidently recall the
Supreme Court's precise holding, and the snapshot carries nothing to confirm
or refine the identification, so the prediction leans on the structural facts
rather than a recalled merits outcome.

Two structural points matter and hold regardless of the exact identification:

1. The docket has an opinion cluster, so this is a **decided historical merits
   case**, not a pending petition awaiting a cert-stage forecast.
2. In the early 1870s Supreme Court review came by **writ of error or appeal as
   of right**, not by petition for certiorari. There was no discretionary
   "grant" stage at all, which makes a `granted` label even less likely here
   than for a later case where certiorari was in fact granted.

## Legal question and governing standard

The event asks for the disposition of the petition
(granted/denied/granted-in-part/dismissed/withdrawn/other). For a historical
merits case the operative question is not a live cert-stage forecast but how
the pipeline's reconciler labels a decided merits case from the
writ-of-error era.

## Mapping to the event's disposition labels

Corpus base rates (`fedcourts stats --court scotus`, 296 resolved events) show
how the pipeline actually labels this population of sparse opinion-import
SCOTUS dockets: **`other` 78.4%, `dismissed` 15.9%, `denied` 4.4%, `granted`
1.4%**. Spot-checking the rare `granted` labels (`fedcourts query --court
scotus --disposition granted`) shows they attach to cases whose opinions
themselves grant something — petitions for prohibition or mandamus, or relief
on the merits — not to ordinary writ-of-error or certiorari merits cases. The
`dismissed` labels attach largely to appeals and writs of error dismissed for
want of jurisdiction, which is a live possibility for an 1870s case but not
one the snapshot lets me confirm.

## Calibration

- `granted = 0`, `probability = 0.03`: the corpus-wide grant share is 1.4%,
  and this case's era had no discretionary grant stage for a reconciler's
  grant-of-certiorari language to latch onto. I set P(granted) slightly above
  the raw base rate only to cover residual identification and labeling
  uncertainty.
- `predicted_disposition = other` rather than `dismissed` or `denied`: `other`
  is the realized label for 78.4% of this population, and nothing in the
  snapshot affirmatively signals a jurisdictional dismissal. Confidence 0.6
  reflects the label-mapping risk — `dismissed` is the main alternative given
  the era's jurisdictional-dismissal practice and its 15.9% share.
- **No per-judge votes.** With the identification resting on the caption alone
  and no confidently recalled holding, per-justice votes for the Chase Court
  would be speculation; I omit them.
