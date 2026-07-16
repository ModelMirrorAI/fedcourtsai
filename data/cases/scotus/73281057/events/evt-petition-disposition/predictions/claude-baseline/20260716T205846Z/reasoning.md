# PhRMA v. O'Day (No. 25-1018) — cert disposition prediction

**Bottom line: P(grant, GVR included) = 0.45; single most likely disposition = denied,
but this is close to a coin flip and well above the ordinary paid-petition rate.**

## The case

PhRMA's facial challenge to Oregon HB 4005, the Prescription Drug Price
Transparency Act, which compels drug manufacturers to file narrative
justifications for price increases and requires the State to publish the
reports — including trade secrets — whenever it deems publication in "the
public interest." The district court struck the law down on both First
Amendment and Takings grounds; a divided Ninth Circuit panel reversed
(*PhRMA v. Stolfi*, 153 F.4th 795 (9th Cir. Aug. 26, 2025), Bea, J.,
dissenting on the First Amendment claim), and rehearing en banc was denied
(Oct. 23, 2025).

Questions presented:

1. Whether a "government reporting requirement" gets only intermediate First
   Amendment scrutiny — and satisfies it — whenever it targets
   "product-specific" information to correct "information asymmetries."
2. Whether businesses in "highly regulated" industries categorically lack
   reasonable investment-backed expectations in their trade secrets for
   Takings Clause purposes.

## Base-rate anchors (committed statpack)

- Modern discretionary-cert petitions overall: grant ≈ 3% (Term 2025 est. 2.5%).
- Paid petitions, Term 2025: est. grant rate 5.4% (statpack.json fee-class detail).
- Ninth Circuit originators (selected slice): granted 16.5%.
- **CVSG bucket: granted 27.1%, denied 71.2% (n=59 resolved)** — the dominant
  cut for this case. (No salience-band section exists in the committed
  statpack, so the CVSG/relist cuts are the anchor.)

## Signals in the docket (all pre-decision; snapshot of 2026-07-16)

Strongly grant-positive:

- **CVSG on June 22, 2026**, issued at the petition's *first* conference
  (distributed June 2 for the June 18 conference) — the classic signal that
  several Justices are seriously interested. The corpus CVSG bucket grants at
  27.1%; published studies of CVSG'd paid petitions put the post-CVSG grant
  rate in the ~35–42% range.
- **Response requested (Mar. 30, 2026)** after Oregon initially waived — an
  earlier, independent signal of interest.
- Divided, published Ninth Circuit opinion with a vigorous dissent (Bea, J.),
  en banc rehearing denied.
- Asserted splits: on QP2, the en banc First Circuit's *Philip Morris v.
  Reilly* (2002) — compelled public disclosure of tobacco ingredient trade
  secrets held a facial taking — is a genuinely close analog decided the
  opposite way, and the Federal Circuit treats "highly regulated industry" as
  one factor, not a bar. On QP1, tension with the Second Circuit (*Amestoy*)
  and D.C. Circuit (*NAM v. SEC*) on whether correcting information
  asymmetry alone is a substantial interest.
- Doctrinal receptivity: then-Judge Kavanaugh's *American Meat Institute*
  concurrence rejected exactly the "information asymmetry" rationale the
  Ninth Circuit adopted; Justice Thomas has repeatedly urged reconsidering
  reduced scrutiny for compelled commercial disclosures; the Court has been
  active in both compelled-speech (*NIFLA*, *303 Creative*) and takings
  (*Horne*, *Cedar Point*, *Knick*) cases.
- Elite Supreme Court counsel (Allon Kedem, Arnold & Porter; Erin Murphy for
  amicus X.AI), paid petition, clean vehicle (facial challenge resolved on
  cross-motions for summary judgment, published opinion, pure questions of
  law), and recurring importance — many states have similar drug-price
  transparency laws (Nevada, California) and analogous narrative-disclosure
  mandates are spreading to AI, climate, and VC reporting (the X.AI
  cert-stage amicus underscores the cross-industry stakes).

Grant-negative:

- The modal outcome even for CVSG'd petitions is denial (71% in the corpus;
  ~60% in the broader literature). The Court usually follows the SG's
  recommendation, and the SG's position here is genuinely uncertain: the
  federal government operates vast mandatory reporting regimes (SEC, FDA,
  IRS) and has itself pursued drug-price disclosure mandates (cf. *Merck v.
  HHS*, 962 F.3d 531 (D.C. Cir. 2020)), and the current administration's
  drug-pricing agenda is adverse to PhRMA — all reasons the SG may resist a
  strict-scrutiny rule for reporting requirements or find vehicle-level
  reasons to recommend denial.
- The QP1 split is softer than the petition suggests: *Amestoy* is a
  1996 labeling case, and *American Meat Institute* upheld the disclosure at
  issue (the strongest language is a concurrence). Oregon's BIO (filed
  May 28, not provisioned as text) presumably presses these
  distinctions.
- No relists-with-outcome yet: the CVSG defers disposition until the SG
  files (likely late 2026), so the disposition remains genuinely open.

## Probability

Starting from the CVSG anchor (~27% corpus, ~35–40% literature) and adjusting
up for the unusually strong stack of secondary signals (response requested,
divided published panel, en banc denial, a near-on-point en banc circuit
conflict on QP2, elite counsel, doctrinal receptivity of the current
majority): P(grant) ≈ 0.45. Roughly: if the SG recommends a grant on either
QP (~45–50% likely given the office's institutional stake in reporting
regimes), the Court grants ~75–80% of the time; on a deny recommendation, a
grant over the SG's objection still happens ~15% of the time in cases the
Court cared enough to CVSG.

A GVR is essentially off the table (no intervening decision pending), and
dismissal/withdrawal is negligible, so the disposition mass is ~0.55 denied /
~0.45 granted (plenary, possibly limited to one QP). Since denial remains
marginally more likely, `granted = 0` and `predicted_disposition = denied`,
with `probability = 0.45` carrying the real signal: this petition is roughly
15–20× more likely to be granted than the average paid petition.

Timing note: given the June 2026 CVSG, the disposition will likely not come
until the SG files (typically ~5–11 months), i.e. early-to-mid OT2026.

## Inputs used

Provisioned snapshot (`record/snapshots/2026-07-16.json`), the event
definition, `record/documents/questions-presented.txt` and
`record/documents/petition.txt` (full 44-page petition text). No
brief-in-opposition text was provisioned (the BIO appears on the docket
May 28, 2026 but was not fetched), so the respondent's counterarguments are
inferred from the docket posture rather than read directly. Corpus base
rates from the committed `metrics/statpack.md`/`statpack.json`; priors and
context per `retrieval.md`. Mode: `forward` (pending case; CVSG outstanding
— no disposition exists to leak).
