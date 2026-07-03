# Bartemeyer v. Iowa — evt-petition-disposition

**Prediction: not granted (granted = 0), P(granted) = 0.03, predicted disposition
`other`, confidence 0.7.**

## What the snapshot contains

The 2026-07-03 snapshot is a sparse historical CourtListener docket (bulk-import
source, no PACER lineage): case name *Bartemeyer v. Iowa*, court `scotus`, one
associated opinion cluster, and **no docket entries, no filing/argument/decision
dates, no docket number, and no petition documents**. The only case-specific
facts available from the snapshot are the caption, the court, and the existence
of a decided opinion cluster.

## What the case is

The caption and docket shape identify this as the historical case *Bartemeyer v.
Iowa*, 85 U.S. (18 Wall.) 129 (1874) — a writ of error to the Supreme Court of
Iowa, not a modern certiorari petition. Bartemeyer was convicted of selling
intoxicating liquor in violation of Iowa's prohibition statute and argued, in
the immediate wake of the *Slaughter-House Cases*, that the statute violated the
Fourteenth Amendment. This identification is background legal knowledge (the
kind of precedent context the contract permits), not a new docket fetch; I note
it plainly because it does most of the work here.

## Legal question and governing standard

Whether a state statute prohibiting the sale of intoxicating liquors deprives
the seller of a privilege or immunity of United States citizenship, or of
property without due process, under the then-new Fourteenth Amendment. Under
*Slaughter-House* (1873), the privileges-or-immunities argument was foreclosed:
regulating or prohibiting the liquor trade is a core exercise of the state
police power. The Court (Miller, J.) affirmed the judgment below, holding the
sale of liquor is not a privilege of national citizenship and that the
property/due-process claim (liquor owned before the statute's passage) was not
properly presented on the record. The plaintiff in error lost outright.

## Mapping to the event's disposition labels

The event asks for a petition disposition from the enum
granted/denied/granted-in-part/dismissed/withdrawn/other. A 19th-century merits
case resolved by affirmance fits none of the grant/deny labels directly.
Corpus base rates (`fedcourts stats --court scotus`, 296 resolved events) show
how the pipeline actually labels these: **`other` 78.4%, `dismissed` 15.9%,
`denied` 4.4%, `granted` 1.4%**. An affirmance against the petitioner is
plainly not `granted` on any mapping, and by the corpus's realized labeling it
most likely reconciles to `other`.

## Calibration

- `granted = 0`, `probability = 0.03`: the corpus-wide grant share for resolved
  SCOTUS events is 1.4%, and my identification of the case as a known
  affirmance pushes the same way; the residual 3% covers the chance I have
  misidentified the docket or that the reconciler maps affirmance oddly.
- `predicted_disposition = other` rather than `denied`: this choice is driven
  by the pipeline's labeling convention (78% `other`) more than by legal
  uncertainty — the legal outcome (petitioner loses, judgment affirmed) is not
  in real doubt. Confidence 0.7 reflects that label-mapping risk.
- **No per-judge votes.** The decision was unanimous in the judgment (with
  concurrences by Bradley and Field), but it was decided during the
  Chase-to-Waite transition and I am not certain of the exact participating
  bench, so I omit `votes` rather than guess names.

## Data-quality note

The snapshot alone (caption + empty docket) would not support a grounded
prediction; without background knowledge of this famous case, the only honest
prediction would be the raw corpus base rate. See `flags.json`.
