# Oregon, et al. v. Paul Maney, et al. — No. 25-960 (evt-petition-disposition)

## Bottom line

**Predicted disposition: dismissed.** `granted = 0`, `P(granted) ≈ 0.01`,
confidence 0.9. The docket's final entry — a **joint motion to dismiss the
petition, submitted June 30, 2026** — makes a Rule 46 dismissal by agreement
the overwhelmingly likely outcome, mooting what had been a live (and mildly
grant-flavored) cert posture.

## The case

Oregon and seven current or former Department of Corrections officials seek
review of the Ninth Circuit's decision (No. 24-2715, June 30, 2025; rehearing
denied September 5, 2025) affirming the district court's denial of qualified
immunity in *Maney v. Oregon*, the class action over Oregon's COVID-19
response in its prisons (D. Or. No. 6:20-cv-00570-SB). The questions
presented (from the provisioned QP text) are:

1. Whether the Eighth Amendment requires state corrections leadership to
   implement an overall "reasonable" statewide response to a public-health
   emergency in the aggregate, across multiple years and facilities; and
2. Whether it was clearly established, for qualified-immunity purposes, that
   Oregon's overall COVID-19 response between March 2020 and May 2022 would
   constitute cruel and unusual punishment, despite a June 2020 district-court
   ruling that the response met constitutional standards.

The governing standards are the Eighth Amendment deliberate-indifference
framework (*Farmer v. Brennan*) and the qualified-immunity
clearly-established-law inquiry (*Ashcroft v. al-Kidd*; *Taylor v. Riojas*
line on obviousness). The petition attacks the Ninth Circuit's aggregation of
a multi-year, multi-facility response into a single "reasonableness" liability
theory, and its finding that the law was clearly established despite an early
contrary district-court ruling.

## What the docket shows (snapshot 2026-07-16)

- Paid petition by a State (Oregon DOJ Appellate Division; SG Paul L. Smith
  counsel of record), filed February 2, 2026 after a Kagan-granted extension;
  docketed February 13, 2026.
- Respondents **waived** a response (March 16, 2026); petition distributed for
  the April 17, 2026 conference.
- **April 2, 2026: the Court called for a response** (CFR) — a genuine signal
  that at least one chamber saw something in the petition; a waived-response
  denial was the default path and the Court declined to take it.
- Response deadline extended to July 6, 2026.
- **June 30, 2026: "Motion of Oregon, et al. to dismiss submitted"** — the
  filed document is captioned as a *joint* motion to dismiss
  (`MANEY-JOINT MODM 25-960 Paul.pdf`). No brief in opposition was ever filed.

## Why "dismissed" and why the probability is where it is

A petitioner's joint/agreed motion to dismiss its own petition is governed by
Supreme Court Rule 46.1: when all parties agree, **the Clerk enters the
dismissal without referring the motion to the Court**. It is about as close to
a mechanical disposition as the Supreme Court's docket offers. The natural
reading is that the parties settled the underlying litigation (the motion
arrived days before the BIO would have come due), and Oregon — the petitioner
— is itself asking to dismiss, so there is no adverse party with an incentive
to resist.

Residual uncertainty (~5–8%) covers only: the motion being withdrawn or the
settlement collapsing before the Clerk acts, or the docket entry meaning
something narrower than it appears. Even in those branches, the petition's
grant odds were modest: a CFR roughly triples-to-quadruples a paid petition's
chances (corpus statpack: CVSG'd/flagged petitions grant ~27% vs ~3% baseline
for no-signal petitions; a bare CFR is a weaker signal than a CVSG), but these
QPs are heavily vehicle-specific ("Oregon's overall response … between March
2020 and May 2022"), fact-bound, and interlocutory in flavor — the sort of
splitless error-correction QI petition the Court routinely denies or, at most,
holds. Weighting: ~0.93 dismissed, ~0.06 denied (if the motion fails and the
Court then denies), ~0.01 granted in any form. Hence `granted = 0`,
`probability = 0.01`, `predicted_disposition = dismissed`.

Corpus base rates corroborate the anchor: modern discretionary-cert petitions
resolve ~94.9% denied / ~3.1% granted / ~2.0% dismissed overall, and the
dismissed slice is precisely the settled/withdrawn population this docket now
joins. Five recent dismissed-petition priors pulled via `fedcourts query` all
show the same shape: a live petition short-circuited before or shortly after
conference, no merits action.

## Big-case score

0.4. If the Court *had* decided it, a ruling on aggregate-theory Eighth
Amendment liability and clearly-established law for statewide emergency
responses would have mattered to every state corrections system and to
pandemic-era retrospective litigation generally — genuine stakes, a State
petitioner, a certified damages class of Oregon inmates. But the questions are
framed around Oregon's specific record, and the settlement itself signals the
parties valued closure over precedent. Notable, not landmark.

## Inputs used

- Provisioned snapshot `record/snapshots/2026-07-16.json` (the docket
  proceedings above).
- Provisioned documents: `questions-presented.txt` and `petition.txt`
  (QPs, parties, related proceedings, petition structure).
- Committed `metrics/statpack.md` base rates; five `fedcourts query` priors
  (see `retrieval.md`).
- Mode: `forward` (`record/context.json`). No outcome for this event exists in
  the snapshot; the joint motion to dismiss is pre-disposition record, not
  leakage — the disposition itself has not been entered.
