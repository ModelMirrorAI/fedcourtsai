# Pesta v. Bloomberg, No. 25-1337 — cert petition disposition

**Prediction: denied. P(grant, GVR included) = 0.02.**

## The case

Bryan Pesta, a tenured psychology professor at Cleveland State University,
was stripped of tenure and fired after a university research-misconduct
proceeding that followed his 2019 publication of a study on "global ancestry
and cognitive ability" using restricted NIH data. He sued under § 1983 for
First Amendment retaliation. The Northern District of Ohio granted summary
judgment to the university defendants, holding he was terminated for research
misconduct (data-access violations), not the content of his speech, with an
alternative holding under *Garcetti v. Ceballos*. The Sixth Circuit affirmed
on causation grounds in an **unpublished** opinion (2025 WL 3094128, Nov. 4,
2025) without reaching the *Garcetti* question; rehearing en banc was denied
December 29, 2025.

The petition (filed at the 90-day deadline, docketed June 1, 2026) presents
three questions: (1) whether *Pickering* originally incorporated the
*Sullivan* actual-malice standard as a threshold the State must clear before
balancing; (2) whether that standard answers the academic-freedom question
left open in *Garcetti*; and (3) whether balancing was properly applied on
these facts.

## Docket signals (snapshot 2026-07-18)

- **Paid** petition, Term 2025 (No. 25-1337).
- Respondents **waived** the right to respond (June 25, 2026); the Court has
  **not called for a response** as of the snapshot.
- **Distributed July 1, 2026 for the September 28, 2026 "long conference"**.
- No amicus briefs on the docket, no CVSG, zero relists (pre-conference).
- Counsel of record is a solo practitioner (Goshen, NY), not a Supreme Court
  specialist; no institutional academic-freedom litigant (e.g., FIRE) appears.

The Court virtually never grants a petition on which the respondent waived
and no response was requested; a grant path here requires a CFR at or before
the long conference, then relists — none of which has happened yet.

## Merits of the cert case

**Against grant (dominant):**

- **Vehicle problem.** The Sixth Circuit affirmed on *causation* — Pesta was
  fired for research misconduct, not his speech — and never reached the
  *Garcetti*/academic-freedom issue. All three QPs sit behind an independent,
  factbound threshold holding, so the Court could not cleanly reach them.
- **QP1 is idiosyncratic.** The claim that *Pickering* adopted *Sullivan*
  malice as a mandatory pre-balancing hurdle is a creative reading pressed by
  few courts; the "split" invoked (*Johnson v. Multnomah County*, 9th Cir.
  1995) is thirty years old, and the petition concedes it "is not quite posed
  as it is here." That is not a developed, live conflict.
- **QP3 is explicit error correction** ("whether balancing was properly
  weighed here"), which the Court does not grant to perform.
- **Unpublished decision below** — no precedential conflict created.
- Long-conference distribution and summer waiver posture both sit in the
  lowest-yield segment of the docket.

**For grant (modest):**

- The *Garcetti* academic-freedom question (QP2) is genuinely open and
  recurring; individual justices (e.g., Justice Thomas, cited in the petition
  via *MacRae v. Matthews* (2025)) have flagged interest in the area, and the
  petition cites fresh circuit-level activity (*Jorjani*, 3d Cir. 2025;
  *Hussey*, 1st Cir. 2025). A CFR from chambers interested in the issue is
  conceivable.
- Paid, counseled petition with a politically salient academic-freedom
  narrative that could yet attract amicus support before the conference.
- A CourtListener check found no pending SCOTUS merits case on
  *Pickering*/*Garcetti* employee speech, so there is no hold/GVR vehicle —
  the realistic disposition menu is plenary grant vs. outright denial, and
  GVR probability is negligible.

## Base rates and calibration

From the committed statpack (live/historical slice, denial-reweighted):

- Modern discretionary-cert grant rate: ~3% overall; **Term 2025: 2.5%**
  overall, **paid petitions 5.4%**, IFP 1.1%.
- Sixth Circuit petitions: granted 3.5%.
- Zero-relist petitions: granted 0.8% (this case's relist count is not yet
  realized, but the no-CFR, respondent-waiver posture is the classic
  precursor of the zero-relist bucket).
- CVSG petitions grant at 27%, but there is no CVSG here and the QPs make one
  very unlikely.

Anchoring on the paid-petition rate (~5%) and adjusting down for the
unpublished decision below, the causation-based vehicle defect, the
idiosyncratic lead theory, the factbound QP3, no response requested plus a
respondent waiver, no amicus support, and long-conference distribution — and
up slightly for the genuinely open *Garcetti* question and possible CFR — I
land at **P(grant) ≈ 0.02** and a predicted disposition of **denied**.

## Big-case score

0.45. If the Court took this case it would be a major First Amendment
decision — resolving the *Garcetti* academic-freedom carve-out with a
race-and-intelligence research backdrop that already drew national
higher-education press. But the case itself is a single-plaintiff employment
dispute decided in an unpublished opinion, so its stakes are moderate rather
than front-page.

## Inputs used

Provisioned snapshot (`record/snapshots/2026-07-18.json`), the petition's
questions-presented section and full petition text under `record/documents/`
(no brief in opposition exists — respondents waived), the committed
`metrics/statpack.md`/`.json`, one `fedcourts query` for corpus priors, and
two CourtListener MCP searches (see `retrieval.md`). Mode: `forward`.
