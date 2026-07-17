# Gomez v. Ryan, No. 25-1258 — petition disposition

**Prediction: denied. P(grant, GVR included) ≈ 0.002.**

## What the record shows

The provisioned snapshot (`record/snapshots/2026-07-17.json`, docketed May 6,
2026, Term 2025, paid) is the primary basis for this prediction. The one
provisioned document, the petition PDF, was fetched but carries
`empty_text: true` — a 26-page scan with no text layer — so the questions
presented are not readable; the analysis below rests on the docket metadata,
which is unusually informative here:

- **Pro se petitioner.** John Paul Gomez of Pittsburgh, PA is his own counsel
  of record, filing from a residential address. The case is nominally *paid*
  rather than IFP, but it carries none of the markers of a
  counseled petition (no firm, no amicus support, extension application and
  petition filed as scans).
- **The respondents are judicial officers.** The waiver of response names
  "Judge Kelly Riddle (substituted for Retired Judge John Nau); the late
  Honorable Dan Favreau; Clerk of Court Ashley Reiter (substituted for retired
  Clerk Karen Starr)," represented by a solo/small firm in Ironton, Ohio
  (Lawrence County). A federal suit by a private individual against state-court
  judges and a clerk over their official acts is the classic profile of a
  § 1983 action barred by absolute judicial and quasi-judicial immunity (and,
  where the relief sought is review of state judgments, by
  *Rooker–Feldman*). These doctrines are settled; petitions in this posture
  present no plausible circuit conflict.
- **The Sixth Circuit disposed of the appeal below on December 2, 2025**
  (No. 24-3840). The decision does not appear in CourtListener's opinion
  index, and the appellate RECAP docket has no purchased entries — consistent
  with an unpublished, non-precedential order affirming a dismissal. An
  unpublished decision applying settled immunity law is close to the weakest
  possible cert vehicle.
- **Respondents waived the right to respond** (May 13, 2026), and as of the
  snapshot the Court has not requested a response. The Court's uniform
  practice is to call for a response before granting; a petition that reaches
  conference on a waiver, with no CFR, is not on a grant track.
- **Distributed June 17, 2026 for the September 28, 2026 conference** — the
  "long conference," where the summer's accumulated petitions are cleared and
  denial is the overwhelming norm. Zero relists so far (none possible yet;
  the first conference has not occurred).

## Base rates and adjustment

From the committed `metrics/statpack.md` (live/historical slice,
denial-reweighted):

- Modern discretionary-cert anchor: **367 granted / 11,712 resolved ≈ 3.1%**
  overall; Term 2025 row estimates a **2.5%** grant rate.
- Relist bucket 0: **granted 0.8%** (repeated relists are the classic
  pre-grant signal; this case has none).
- CVSG: none (the `none` bucket runs ~3.0% granted; no upward adjustment).
- Originating circuit CA6: granted 3.5% — roughly the anchor, no adjustment.

The 0.8% zero-relist figure is itself an overestimate for this cell because it
averages over counseled petitions with real QP conflicts. Conditioning further
on (a) pro se filing, (b) respondents who waived with no CFR from the Court,
(c) an unpublished decision below applying settled absolute-immunity doctrine,
and (d) long-conference distribution, the realistic grant probability sits
well below the bucket rate. I set **P(grant) = 0.002**, with `denied` as the
predicted disposition (dismissal/withdrawal is possible but has no docket
signal here). No intervening decision or mootness event is visible that would
make a GVR the modal grant form, so `gvr` is not predicted.

Expected timing: denial on the order list following the September 28, 2026
conference (early October 2026).

## Big-case score

0.02. A private dispute with local judicial officers; even if granted it would
resolve nothing of general significance, and there is no visible press,
amicus, or institutional interest.

## Degradations

- The corpus query sidecar was unreachable (`fedcourts query` timed out
  against the local service), so no similar-case priors could be retrieved;
  the prediction leans on the committed statpack and the docket record. Per
  the contract, a degraded upstream degrades the cell, never blocks it.
- The petition's text could not be extracted (scanned filing, no text layer;
  flagged in `flags.json`), so the questions presented were not read. Given
  the strength of the structural signals, this raises the variance of the
  estimate only slightly.
