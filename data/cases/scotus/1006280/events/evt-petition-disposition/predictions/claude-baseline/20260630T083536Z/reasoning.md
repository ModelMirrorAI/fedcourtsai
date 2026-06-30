# Prediction reasoning — scotus/1006280, evt-petition-disposition

## The legal question

The event (`kind: petition`, `decision_target: disposition`, title *Consolidated
Rail Corporation v. National Assn. of Recycling Industries, Inc.*) asks how the
Supreme Court of the United States disposed of the petition in this matter. The
outcome space is the standard disposition enum (granted / denied /
granted-in-part / dismissed / withdrawn / other), with `granted` as the binary
target and `probability` as P(granted). At this posture the petition is a
petition for a writ of certiorari, so **granted** means cert granted (the Court
took the case, whether for plenary review or for a summary per curiam
disposition).

## Governing standard

Certiorari is discretionary (Supreme Court Rule 10), and the unconditioned base
rate is overwhelmingly denial — the Court grants only a small fraction of
petitions. But the base rate is not the only evidence here: I predict from the
provisioned snapshot
(`data/cases/scotus/1006280/record/snapshots/2026-06-30.json`), and the snapshot
carries structural identifiers that move the prediction well off the base rate. I
did **not** fetch new docket facts or look up the historical outcome (the very
quantity under evaluation).

## Facts from the snapshot that drive the outcome

The merits record is thin — `docket_entries: []`, and `date_argued`,
`date_filed`, `date_cert_granted`, `date_cert_denied`, and `date_terminated` are
all `null`. But several identifiers on the face of the snapshot carry real signal
(these are not "new facts"):

- **Docket number `80-568`** (`docket_number_raw`, `docket_number_core`
  `80000568`). The sequence number `568` is far below the ~5000 in-forma-pauperis
  threshold, so this is the **paid docket** for October Term 1980. The paid
  docket grants certiorari at a materially higher rate than the IFP docket, and
  the early-1980s Court took a substantially larger merits docket than the modern
  Court.
- **Counseled corporate / regulatory posture.** The petitioner is Consolidated
  Rail Corporation (Conrail) against a national trade association — a
  represented, commercial/regulatory dispute, the profile of case the Court is
  comparatively more likely to take than a pro se prisoner petition.
- **An opinion cluster is present** —
  `clusters: ["…/clusters/110386/"]`. A SCOTUS docket linked to an opinion
  cluster indicates the Court issued a written opinion in the matter. Routine
  cert denials produce no opinion cluster (they are a line in an orders list);
  only the small subset of denials that draw a written dissent generate one. So
  conditioning on the presence of a cluster already filters out the bulk of
  routine denials and shifts the mass toward "the Court acted substantively
  here," i.e. a grant (plenary or summary).

## What pulls the probability back from near-certainty

Unlike the snapshots that justify a near-1.0 grant prediction, this one has **no
`date_argued` and an empty `audio_files`** — there is no positive confirmation
that the case was argued and decided on plenary review. The opinion cluster is
consistent with three scenarios, only the first two of which are grants:

1. A plenary grant whose argument date / audio simply are not populated in the
   upstream record (common for older cases), or a **summary per curiam**
   disposition decided without argument — **grant**.
2. An opinion accompanying a **dissent from denial** of certiorari — **denial**.

The dominant reading for an OT1980 paid-docket, counseled case with a SCOTUS
opinion cluster is a grant (per curiam summary dispositions were a routine
vehicle in this era), but the dissent-from-denial path is a real residual.

## Probability and disposition

- **`predicted_disposition`: granted**, **`granted`: 1**.
- **`probability` (P(granted)): 0.70.** The opinion-cluster signal on a paid
  docket with a counseled corporate posture points clearly toward a grant; the
  absence of argument-date/audio confirmation and the residual
  dissent-from-denial possibility hold it short of the near-certainty reserved
  for snapshots that also show argument and audio.
- **`confidence`: 0.5**, reflecting that the directional call rests on a single
  structural signal (the cluster) rather than a confirmed argument-and-opinion
  record.

I report no per-judge `votes`: the event targets the petition's disposition (a
court-level grant of certiorari), not a merits vote split, and the snapshot
identifies no panel.
