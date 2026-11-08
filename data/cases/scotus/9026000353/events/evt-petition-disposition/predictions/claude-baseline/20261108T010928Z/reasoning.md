# Reasoning — Vasquez v. Guerrero, No. 26-353 (capital, CA5)

**P(grant) = 0.08.**

## Anchor
`record/context.json`: forward mode, band `baseline` (sal-v8), `distribution_count` 1, no CVSG,
`cert_anchor.rate` = 0.0515 (baseline band's pooled `reached` rate, 10 prior Terms). The
statpack's per-Term baseline `reached` rates for 2017–2025 sit at 4–6%, consistent with it.

## Record read
- Snapshot `2026-11-08.json`: petition filed Sep 11 2026, BIO Oct 16 2026, distributed for
  the 12/4/2026 conference. No reply, no amicus, no related-docket staging (`vide_links` empty).
- `questions-presented.txt` / `petition.txt` (truncated at cap in the appendix): whether a
  later-in-time application raising Brady and Napue/Giglio claims the petitioner did not know
  about at first filing is "second or successive" under § 2244(b). The petition relies on
  Panetti, on Justice Sotomayor's writings in Storey v. Lumpkin (2022) and Bernard v. United
  States (2020), and on panels in CA4/6/9/11 criticizing their own circuits' precedent. It
  concedes there is **no clean circuit split**: every circuit to rule follows the CA5 rule, and
  the dissent sits within those circuits. The local DA (Nueces County) has said the conviction
  should be set aside, but the Texas AG controls the federal litigation and opposes.
- `brief-in-opposition.txt`: Texas argues there is no split; that the petition seeks review of
  an unreasoned summary COA denial with several independent grounds (jurisdiction, no valid
  constitutional claim, Bowe v. United States, 607 U.S. 13 on the (b)(3)(E) bar); that the
  filing was built to manufacture a vehicle for the pending No. 25-1246; and that the claims
  were available since trial (a factual fight over ripeness).

## Companion: No. 25-1246 (retrieved from supremecourt.gov — not staged in `record/related/`)
The same petitioner's earlier petition raises the same issue in a different posture. Its docket
shows a **record requested (Aug 11 2026)**, a motion to defer, a letter, a reschedule after
distribution for 11/6, and a new distribution for **12/4/2026** — the same conference as this
petition. So the Court has had one Justice pull the record and is now setting the two petitions
together. That is real attention. It most often goes before a written dissent or statement
respecting denial in a capital case, and less often before a grant or summary action.

## Adjustments
Up from ~5%: capital case; a recurring question at least one Justice has asked to take; the
companion's record request and joint scheduling; this posture partly answers the (b)(3)(E) bar.
Down: no circuit split; review of a summary COA denial with alternative grounds; a disputed
fact on whether the claims were available earlier (Texas says since trial); a two-petition
posture the Court may read as vehicle-shopping; the Court has denied this question repeatedly
(Storey, Bernard). Net: 8%.

## Other claims
- relist-increment 0.35: the companion was already rescheduled once. Joint consideration with
  a record-requested petition raises the chance of another relist, whether for a separate
  writing or a closer look.
- cvsg-increment 0.01: a state habeas case with no federal party.
- summary-disposition-route 0.20 (conditional on grant): plenary review is the natural route
  for a statutory question this broad. Some room is left for a summary vacatur on the COA
  ground.
- dissent-from-denial 0.35 (conditional on denial): Sotomayor has written on this exact
  question twice, it is a capital case, and the companion's record was requested. The writing
  could also land on the 25-1246 order rather than this one, which caps the number.

## Uncertainty
I cannot see who requested the companion record or why. The petition text is truncated in the
appendix, but the body was read in full. No CourtListener MCP lookups were made.
