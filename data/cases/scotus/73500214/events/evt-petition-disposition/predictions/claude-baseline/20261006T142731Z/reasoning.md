# Why 0.52

## What I read

Provisioned inputs: `record/snapshots/2026-10-06.json` (11 docket entries
through the October 5, 2026 CVSG), `record/context.json` (forward mode, band
`high` under sal-v4, one distribution, CVSG date 2026-10-05, Term 2025),
`event.yaml` (stage cert, moment distribution), and all three provisioned
documents: `questions-presented.txt`, `petition.txt` (43 pages, full text) and
`brief-in-opposition.txt` (40 pages, full text). The committed
`metrics/statpack.md` supplied the base rates.

## Anchor

The band table's `high` column is the registered anchor. Pooling the bracketed
`reached` rate over the eight prior Term rows the table renders (OT2017 to
OT2024, strictly before this case's docket-number Term) gives about 35.0% on a
weighted n of 898. The statpack's CVSG cut for the paid scored segment reads
granted 29.4% plus GVR 5.5%, about 35% grant family, on a small n of 163. The
relist-1 bucket (8.2% granted, 5.1% GVR) is the terminal-count population and
understates a petition that is still live, so I read it only for shape. The
two independent anchors agree at roughly 0.35, and that is my starting point.

## Adjustments up

- The Court has already granted this exact question in this exact case,
  unanimously vacated the Second Circuit, and did so over a Solicitor General
  recommendation to take *Kivett* instead. That is direct evidence that the
  Court finds the issue certworthy and this vehicle acceptable.
- The remand decision is divided, and the majority expressly acknowledges and
  rejects the First Circuit's *Conti* reading of *Cantero*. The BIO does not
  deny the split; it calls it narrow and effectively 1-1.
- The CVSG came after the first conference, which is a stronger signal than the
  bare CVSG cut records, and it signals that at least a substantial bloc wants
  the case considered seriously.
- Cert-stage support from 26 states plus DC and the state bank supervisors, and
  experienced Supreme Court counsel on both sides.
- A second strong vehicle (*Flagstar*, No. 25-1350) and a rehearing petition
  (*Conti*, No. 25-1004) are pending, so the Court can resolve the split this
  Term through any of three doors, and a hold here that ends in a GVR counts as
  a grant on this event's axis.

## Adjustments down

- The BIO's percolation argument has real force: the OCC's Escrow Powers Rule
  and Preemption Determination became effective in June 2026 after the lower
  court decisions, and no court has addressed them. The Solicitor General under
  the current administration will almost certainly defend the OCC's position,
  and may recommend denial to let the regulations be tested first.
- The Court follows the Solicitor General's cert recommendation most of the
  time. Even where the United States recommends a grant, it previously
  preferred *Kivett*/*Flagstar* as the vehicle, and the BIO asks for exactly
  that with a hold here. A hold behind *Flagstar* resolves as a grant only if
  the Court ultimately rules against preemption.
- Second-trip petitions carry some reluctance: the BIO frames the 2024
  decision as an invitation to percolate.

Rough scenario weights I used: SG recommends grant here (alone or with
*Flagstar*) 0.35, with grant probability about 0.9; SG recommends *Flagstar*
with a hold here 0.30, with this petition ending in a GVR about 0.4 of the time;
SG recommends denial 0.35, with the Court granting anyway about 0.25. That sums
to about 0.52, well above the 0.35 anchor, and I committed to 0.52.

## Claims

- `disposition` 0.52, equal to `probability`.
- `relist-increment` 0.97: a CVSG petition is redistributed once the brief of
  the United States arrives; the residual is withdrawal or settlement.
- `cvsg-increment` 0.02: a CVSG is already on the docket, so this claim is
  vacuous for my cell and the harness will mask it; the number is P(a second
  invitation), which is essentially nil.
- `summary-disposition-route` 0.22 conditional on a grant: the GVR path is the
  hold-behind-*Flagstar* scenario; a plenary grant is the modal grant.
- `dissent-from-denial` 0.20 conditional on a denial: a denial would most
  likely follow an SG recommendation to wait for the OCC regulations, and I
  expect the Court to accept that quietly more often than not.

## Big case score

0.6. The stakes are a nationwide preemption standard for 14 states' laws, a
live question about the force of OCC preemption determinations under
Dodd-Frank, and class exposure for the largest mortgage servicers. It is a
major business and federalism case but technical, so not at the top of the
scale.

## Uncertainty and where to discount me

- The decisive unknown is the Solicitor General's recommendation, which will
  not exist for months; my scenario weights for it are judgement, not data.
- I could not check the current status of *Flagstar* (25-1350) or the *Conti*
  rehearing petition (25-1004): the CourtListener MCP server returned HTTP 429
  rate-limit errors on both lookups and the corpus-query priors carried no
  captions. What I know about those dockets comes from the petition and the
  BIO as of August 2026, and whether the Court CVSG'd *Flagstar* alongside this
  case would materially sharpen the hold-versus-grant split.
- The CVSG cut and the high-band pool are small samples (n in the low hundreds
  per Term), so the 0.35 anchor itself carries a few points of noise.
- I carry general knowledge of the 2024 *Cantero* decision from training; it is
  pre-decision context for this petition, not outcome material.
