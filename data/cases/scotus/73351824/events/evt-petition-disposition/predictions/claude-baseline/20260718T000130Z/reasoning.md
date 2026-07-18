# Prediction: N. R., et al. v. Ellison, No. 25-1287 (cert petition disposition)

**Call: deny is still the modal outcome, but this is a genuinely elevated petition — P(any grant, GVR included) ≈ 0.13.**

## The case

Nathan and Kellie Reyelts, non-Indian former foster parents of twin Red Lake
Nation-eligible toddlers with severe medical needs, petition from the
Minnesota Supreme Court's April 9, 2026 judgment (32 N.W.3d 163) affirming the
denial of their motion to intervene in the twins' CHIPS proceeding. Questions
presented (from the provisioned `questions-presented.txt` / petition):

1. Whether ICWA and Minnesota's MIFPA unconstitutionally deny equal protection
   to "Indian" children and to non-"Indian" people who seek custody of them.
2. Whether denying petitioners intervention *because* they made a good-faith
   argument that ICWA/MIFPA are unconstitutional violates the First Amendment.

This is a deliberate sequel to *Haaland v. Brackeen*, 599 U.S. 255 (2023),
which reserved the equal-protection question on standing grounds and (n.10)
said parties injured in state proceedings could raise it there. Counsel of
record is Mark Fiddler — the ICWA-specialist who was on *Adoptive Couple* and
*Brackeen* — joined by Timothy Sandefur of the Goldwater Institute, the most
persistent institutional ICWA challenger.

## Signals pointing toward a grant

- **Call for response.** The respondent GAL waived (May 29, 2026); the case
  was distributed for the September 28, 2026 long conference; and on June 25,
  2026 the Court **requested a response** (due July 27, extended to Aug. 26 on
  respondent's motion). A CFR means at least one chambers is engaged; it
  historically multiplies grant odds several-fold over the paid baseline.
- **Cert-stage amicus support.** Three amicus briefs at the petition stage
  (Academy of Adoption & Assisted Reproduction Attorneys / National Council
  for Adoption; foster parents + Pacific Legal Foundation; Christian Alliance
  for Indian Child Welfare) — a strong salience marker for a paid petition.
- **A question several Justices want.** Thomas and Alito dissented in
  *Brackeen*; Kavanaugh concurred specifically to call the equal-protection
  issue "serious" and to be decided "in an appropriate case." The petition is
  engineered to be that case, and adds an anti-evasion hook (state courts
  manipulating procedure to insulate ICWA from review — *NAACP v. Patterson*,
  *Cruz v. Arizona*) that speaks directly to those chambers.
- **Paid petition, sophisticated presentation**, live circuit/state-court
  disagreement framing (existing-Indian-family doctrine splits), and a
  discrete second question suitable for summary reversal.

## Signals pointing toward a denial

- **The vehicle is compromised — and that is the heart of it.** The Minnesota
  Supreme Court affirmed the denial of *intervention* on state-law
  best-interests grounds, held the Reyeltses were non-parties, and vacated the
  Court of Appeals' constitutional holding. The equal-protection merits were
  never passed on by the final state court. Petitioners must first defeat an
  adequate-and-independent-state-ground bar (the petition devotes a full
  section, II.C, to arguing around it — a telltale weakness). QP1 rides
  entirely on winning QP2 first.
- **Fact-bound, ongoing child-custody posture.** The CHIPS proceeding
  continues; the twins have been moved twice since leaving the Reyeltses
  (the tribal-cousin placement fell through; they are now with their maternal
  grandmother). The Court is historically reluctant to wade into live
  custody disputes, and changed placements erode the remedial upside.
- **The intervention denial is discretionary state procedure.** Even the
  First Amendment question arrives wrapped in a deferential
  abuse-of-discretion posture with an alternative "harmless/independent
  grounds" rationale below.
- **Post-Brackeen restraint.** Since 2023 the Court has not taken up any
  ICWA equal-protection sequel; a CVSG or waiting for a cleaner vehicle (a
  final judgment actually applying ICWA's placement preferences against a
  petitioner on the merits) is a live alternative path. (I could not verify
  the post-2023 petition history via CourtListener this run — the MCP
  server's daily quota was exhausted; see `retrieval.md` — so I weight this
  qualitatively, not on specific verified denials.)
- **Timing.** As of the 2026-07-17 snapshot the petition has zero conference
  relists (it has not yet been conferenced); the strongest pre-grant signal
  (repeated relists) cannot yet be observed.

## Base rates and the quantitative call

From the committed statpack (live/historical slice, denial-reweighted):

- Modern discretionary-cert anchor: grants are ~2.5–3.3% of resolved
  petitions per recent Term.
- **Paid** fee class (this is a paid petition, Term 2025): ~5.4% grant
  (Term 2024: ~6.9%).
- Relist cuts: 0 relists → 0.8%; 1 → 7.6%; 2 → 33.6%; 3+ → 21.8%. Not yet
  observable here (pre-conference).
- CVSG cut: none here (27.1% when present).
- State-court-originated petitions in the sampled slice grant rarely.

Starting from the ~5–7% paid baseline, I adjust **up** for the call for
response after a waiver (the single strongest observable signal on this
docket), three cert-stage amici, elite repeat-player counsel, and a question
with at least three publicly interested Justices; I adjust **down** for the
serious jurisdictional/vehicle defects (non-party posture, AISG exposure,
vacated constitutional holding below), the messy ongoing custody facts, and
the real possibility the Court waits for a merits-posture vehicle. A GVR path
exists in theory but there is no intervening decision to GVR against, so the
grant probability is essentially P(plenary grant, possibly limited to QP2,
plus a small summary-reversal tail).

**P(granted, incl. GVR) = 0.13; predicted disposition: denied** (the single
most likely outcome by a wide margin). If the Court is interested short of
four votes, the likeliest observable trajectory is relists after the BIO
lands (post-Aug. 26), possibly a CVSG — both of which would raise this
number materially on a later snapshot.

## Big-case score

0.8 — if granted and decided, this would be a landmark: the constitutionality
of ICWA's ancestry-based classifications, reserved in *Brackeen*, with
consequences for Indian law's political-classification foundation
(*Morton v. Mancari*), every state ICWA analogue, and child-welfare practice
nationwide. The stakes are high even though the grant odds are modest.

## Inputs used

- Snapshot `record/snapshots/2026-07-17.json` (docket entries, parties,
  paid fee class, CFR and extension entries).
- `record/documents/questions-presented.txt` and `record/documents/petition.txt`
  (379-page filing, truncated text; QP section intact). No brief in
  opposition exists yet — response now due August 26, 2026 — so the
  respondents' vehicle arguments are anticipated, not read.
- Committed `metrics/statpack.md` + per-fee-class detail in
  `metrics/statpack.json`; two `fedcourts query` pulls of recent
  granted/denied SCOTUS priors (see `retrieval.md`).
