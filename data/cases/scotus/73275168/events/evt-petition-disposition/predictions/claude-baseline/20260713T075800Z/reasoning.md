# Poore v. United States, No. 25-227 — cert-petition disposition

**Prediction: granted (P = 0.60), where "granted" follows the pipeline's coding
convention that a GVR — grant, vacate, remand — lands on the granted side. The
modal concrete outcome I foresee is a GVR in light of *Beaird v. United States*,
No. 25-5343, not a plenary merits grant.**

## The legal question

Poore, a § 922(g)(1) felon-in-possession defendant, received a base-offense-level
enhancement because his prior Wisconsin conviction for substantial battery *as a
party to the crime* was classified as a "crime of violence." The guideline text
(U.S.S.G. § 4B1.2(a) (2021)) did not reach inchoate/accessory liability; only
Application Note 1 did. The question presented is whether *Kisor v. Wilkie* and
*Loper Bright v. Raimondo* constrain the *Stinson v. United States* rule of
near-automatic deference to Sentencing Guidelines commentary. The petition
(Neal Katyal, Milbank) documents an acknowledged, entrenched 6–6 circuit split
across all twelve circuits that hear criminal appeals.

## Docket signals in the snapshot

- Paid petition, Term 2025 (No. 25-227), from the Seventh Circuit (unpublished
  order applying *United States v. White* and refusing to revisit deference).
- The government initially **waived** response; the Court **called for a
  response** (Sep 18, 2025) — a classic at-least-one-Justice-interested signal.
- Cert-stage amicus (New Civil Liberties Alliance).
- After full briefing (BIO Nov 19, reply Dec 3), the petition was distributed
  for **ten conferences** (Jan 9 through Apr 17, 2026) — an extreme relist
  chain — and then the distributions **stopped**. No disposition appears
  through the snapshot (docket JSON generated Jul 10, 2026).

## The decisive context: the *Beaird* grant

On **April 20, 2026** — the order day following Poore's last distribution
(the April 17 conference) — the Court **granted certiorari in *Beaird v.
United States*, No. 25-5343**, limited to: "Whether *Stinson v. United States*
still correctly states the rule for the deference that courts must give the
commentary to the Sentencing Guidelines." Because the Solicitor General agrees
that *Kisor* now supplies the standard (the government said the same in its
Poore BIO), the Court appointed an amicus (Anthony Dick) to defend *Stinson*.
*Beaird* is structurally identical to Poore: a § 922(g)(1) sentencing
enhancement that exists only in commentary.

This explains the whole Poore pattern: serial relists while the Court sifted
vehicles on this QP, then silence once *Beaird* was chosen. Poore is now
almost certainly a **hold for *Beaird***, to be disposed of after *Beaird* is
decided (argument fall 2026, decision expected by ~June 2027). Note that this
event therefore probably stays open for about a year.

Why *Beaird* over Poore? The Poore BIO's vehicle attacks are real:
1. **Mootness** — Poore finished his prison term on Nov 7, 2025 (he petitioned
   with <75 days left) and only supervised release remains; though Seventh
   Circuit law (*Pope v. Perdue*) treats the possibility of reduced supervised
   release as preserving the controversy, the SG argued the redressability
   theory is speculative and itself the subject of a circuit split.
2. **Antecedent grounds** — the enhancement actually ran through § 2K2.1's
   commentary (whose incorporation of Application Note 1 Poore never disputed),
   and Wisconsin party-to-a-crime liability requires a consummated substantive
   battery, arguably satisfying § 4B1.2(a)(1)'s elements clause directly under
   *Delligatti* regardless of the note.

Those defects made Poore a poor plenary vehicle, but they matter much less to
the GVR question.

## Probability tree

1. **P(*Beaird* holds that Stinson deference is limited — i.e., the
   petitioner/government side prevails over the appointed amicus): ~0.78.**
   Both parties align against the judgment below; court-appointed amici
   defending abandoned positions usually lose; and the Court's trajectory
   (*Kisor*, *Loper Bright*, the lenity concerns several Justices have voiced
   about Guidelines commentary) points the same way. Amici do occasionally
   win, and a narrow or DIG-style resolution is possible, so not higher.
2. **P(Poore GVR'd | favorable *Beaird*): ~0.75.** Held petitions presenting
   the decided question are GVR'd nearly mechanically under the lenient
   "reasonable probability the lower court would reconsider" standard — the
   Seventh Circuit's *White*/*Stinson* framework would be abrogated. The
   discount reflects the BIO's mootness argument and the two independent
   affirmance grounds, which the SG will re-press against a GVR and which
   could tip the Court to a simple denial.
3. **P(denied | *Beaird* reaffirms Stinson): ~0.95.**
4. Residuals: plenary grant/consolidation ~0.01; dismissal (e.g., on
   mootness) ~0.02.

P(granted, GVR included) ≈ 0.78 × 0.75 + 0.01 ≈ **0.60**.
P(denied) ≈ 0.78 × 0.24 + 0.22 × 0.95 ≈ 0.37; dismissed ≈ 0.02; other ≈ 0.01.

## Base-rate anchor and adjustment

The committed statpack's modern discretionary-cert slice (Term 2025) shows a
**4.9% grant rate** (denial-reweighted; relist and CVSG cuts are unpopulated).
An unconditioned paid petition would sit near that anchor. This cell moves far
off it because of conditioning the anchor cannot see: a called-for response
after waiver, ten relists, and — decisive — a granted companion case on the
identical QP with this petition evidently held for it. The dominant path to
"granted" here is the GVR channel, which the pipeline's cert-signal labeler
(`src/fedcourtsai/pipeline/cert_signals.py`) maps to `granted`.

## Inputs used

Provisioned snapshot (`record/snapshots/2026-07-13.json`), questions-presented
text, full petition text, and full BIO text (all `empty_text: false`,
untruncated); `metrics/statpack.md` for base rates; web retrieval for the
*Beaird* grant (see `retrieval.md`). Mode is `forward`; this case's own outcome
does not exist and was not sought. I have no prior knowledge of this specific
petition's disposition beyond the pre-decision record.
