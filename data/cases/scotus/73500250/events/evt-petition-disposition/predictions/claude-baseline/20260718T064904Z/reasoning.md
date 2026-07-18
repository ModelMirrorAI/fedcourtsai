# Delgado v. United States, No. 25-1347 — cert petition disposition

**Prediction: denied. P(grant, GVR included) = 0.03.**

## The case

Miguel Angel Delgado, Jr., a CBP officer, was convicted after a bench trial in
the Western District of Texas of two counts under 18 U.S.C. § 242 (deprivation
of rights under color of law, felony-enhanced by bodily injury) and one count
under 18 U.S.C. § 1519 (falsifying a use-of-force report), arising from two
use-of-force incidents at El Paso ports of entry. The Fifth Circuit affirmed in
a published opinion, *United States v. Delgado*, 168 F.4th 752 (5th Cir. Mar. 3,
2026). The counseled, paid petition (filed May 28, 2026) presents four
questions:

1. Whether the Fifth Circuit's excessive-force analysis was temporally confined
   in violation of *Barnes v. Felix*, 605 U.S. 73 (2025);
2. Whether *Screws v. United States* requires subjective criminal intent for
   § 242 willfulness, versus the objective-unreasonableness evidence the Fifth
   Circuit relied on (a claimed circuit split);
3. Whether § 242's "bodily injury" felony enhancement requires more than
   de minimis injury (a claimed three-way circuit split);
4. Whether the § 1519 conviction can stand if the § 242 predicates fall
   (derivative).

## Docket signals (snapshot of 2026-07-18)

- The United States **waived its right to respond** (June 30, 2026). The Court
  does not grant certiorari without a response on file, so a grant would first
  require a call for a response (CFR) — a step that has not happened.
- **Distributed for the September 28, 2026 long conference** — the summer-list
  conference at which the overwhelming majority of petitions are denied. A
  single distribution; no relists yet (corpus priors show granted petitions
  typically carry multiple distributions).
- No CVSG, no amicus support noted on the docket.
- Paid, counseled petition from a published court of appeals opinion — the
  strongest fee-class and posture, but a small-firm filing without repeat
  cert-stage counsel.

## Base rates and adjustment

From the committed statpack (modern discretionary-cert slice,
denial-reweighted): overall grant rate ~2.5–3.3% per recent Term; **paid**
petitions grant at ~5.4–8.0% (OT2023–OT2025); CA5-originated petitions ~4.8%;
petitions with zero relists grant at ~0.8%, and no CVSG ~3.0%. The paid class
puts the anchor near 5–7%; the waiver-plus-no-CFR posture and long-conference
distribution pull well below that anchor, because the realistic grant path
(CFR → response → relists → grant) is long and each step is unlikely.

## Merits assessment of certworthiness

- **QP2 (Screws willfulness)** is the petition's strongest claim: the tension
  in *Screws* between "specific intent" and "need not think in constitutional
  terms" is real and long-noted, and the petition frames a majority/minority
  split. But the Court has declined many cleaner vehicles over decades (a
  CourtListener check confirms no modern SCOTUS opinion revisiting the § 242
  willfulness standard), and here the question arrives wrapped in a
  sufficiency-of-the-evidence challenge to bench-trial findings — a weak
  vehicle, since the Fifth Circuit's willfulness discussion can be read as
  ordinary circumstantial proof of subjective intent (concealment and false
  reports are classic consciousness-of-guilt evidence, not purely "objective"
  proof).
- **QP1 (Barnes evasion)** is error correction: the decision below *postdates*
  *Barnes* (so no GVR path — GVR requires an intervening decision), and the
  claim that the court "effectively" confined its analysis while nominally
  surveying context is a fact-bound reading of one opinion, the kind of
  application dispute the Court leaves alone.
- **QP3 (bodily injury threshold)** asserts a shallow, rarely-outcome-
  determinative split; the injuries here (concussion-like symptoms; a nose
  laceration) would satisfy even the stricter greater-than-de-minimis standard,
  making the split academic on these facts.
- **QP4 is derivative** of QPs 1–2 and adds no independent grant reason.
- The interlocking structure — each QP depends on the others ("analytically
  defective ... predicate findings") — is itself a vehicle problem.

There is a modest chance the long conference produces a CFR given the counseled
presentation of a genuine recurring issue (perhaps ~10–15%), and a grant
conditional on that path remains unlikely (~15–20%), yielding roughly 2–3%
overall; I round to **0.03**. No plausible GVR basis exists, so the residual
grant probability is essentially all plenary. The likeliest disposition by a
wide margin is a **denial**, most plausibly at or shortly after the
September 28, 2026 conference.

## Inputs used

Snapshot `record/snapshots/2026-07-18.json`; provisioned
`questions-presented.txt` and `petition.txt` (74 pp., full text; no
brief-in-opposition exists — response waived); `metrics/statpack.md` /
`statpack.json`; two corpus `fedcourts query` pulls and two CourtListener MCP
searches (see `retrieval.md`). Mode: `forward` — no outcome exists; nothing
outcome-revealing was encountered.
