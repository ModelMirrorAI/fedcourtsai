# Daisey Trust v. FHFA, No. 25-1144 — cert disposition prediction

**Prediction: deny. P(any grant, GVR included) = 0.05.**

## The case

Petitioners are Nevada investment entities (Daisey Trust, Cape Jasmine Ct.
Trust, Saticoy Bay LLC Series 10007 Liberty View) that bought homes at HOA
lien-foreclosure sales in 2012–2013, lost earlier state-court quiet-title
fights with the enterprises' loan servicers, and — facing foreclosure on the
enterprises' surviving mortgage liens — sued FHFA in the District of Nevada in
2023 on a new theory: FHFA's self-funding mechanism, 12 U.S.C. § 4516, violates
the Appropriations Clause and the nondelegation doctrine, so its
conservatorship-funded foreclosure activity is unconstitutional. The district
court found standing but rejected the merits; the Ninth Circuit affirmed in a
published opinion (163 F.4th 1208, Jan. 2, 2026), reading *CFPB v. CFSA*, 601
U.S. 416 (2024), to require only an identified source and purpose for agency
funding, and finding "sufficient to provide for reasonable costs … and
expenses" an adequate intelligible principle under *FCC v. Consumers'
Research*, 606 U.S. 656 (2025).

The three questions presented (from the provisioned QP text): (1) does
§ 4516 violate the Appropriations Clause for lack of a cap, sum certain, or
ascertainable limit — the feature the *CFSA* Court repeatedly noted CFPB's
funding had and FHFA's lacks; (2) does § 4516(f)(2)'s "shall not be construed
to be Government or public funds or appropriated money" label violate the
Clause; (3) does § 4516's "sufficient … reasonable" standard violate the
nondelegation doctrine.

## Signals for a grant

- **The Court called for a response.** The SG waived (Apr. 15, 2026); the
  petition was distributed for the May 14 conference; on May 5 the Court
  requested a response. At least one chambers found the petition worth a look.
  That is the single strongest signal here and lifts the petition well above
  the run of paid CA9 petitions.
- **Genuinely open question.** *CFSA* upheld CFPB's funding while repeatedly
  noting its statutory cap; whether an *uncapped* assessment scheme satisfies
  the Clause is a fair reading of what *CFSA* left open, and the petition
  (Brownstein Hyatt; a capable Supreme Court presentation) frames it cleanly
  as conflict-with-*CFSA* or first-impression importance under Rule 10(c).
- **Stakes.** FHFA sits atop entities with $8T+ in assets; a ruling for
  petitioners would put every self-funded regulator's structure in play.

## Signals against a grant (they dominate)

- **No circuit split — and circuit agreement.** The BIO notes petitioners do
  not claim a conflict. My retrieval confirms only two courts of appeals have
  touched FHFA-funding challenges (the Fifth Circuit's *Collins v. Treasury*,
  83 F.4th 970 (2023), and the Ninth Circuit here), and both rejected them.
  The Court denied cert on the *Collins* remand's funding theory post-*CFSA*.
- **The theory rides the dissents.** The cap requirement comes from the
  *CFSA* dissent (Alito, J., joined by Gorsuch, J. — the only two votes for
  it, and the majority's "source and purpose are all that is required"
  language is squarely against it); the numerical-limit nondelegation theory
  comes from the *Consumers' Research* dissent, rejected 6–3 just one Term
  ago. The Court rarely grants to revisit a framework it announced two Terms
  earlier, on a vehicle asking it to adopt the dissents.
- **The SG's BIO stacks vehicle problems**: a live standing challenge
  (foreclosure injury not traceable to the funding mechanism because the
  enterprises' servicers, not FHFA, run day-to-day foreclosures — the
  government re-raises it as an independent Article III obstacle), a
  preserved-but-unaddressed claim-preclusion defense from petitioners' lost
  state-court quiet-title suits, and a preservation problem on QP2
  (§ 4516(f)(2) mentioned in one sentence each in the CA9 opening and reply
  briefs, unaddressed by the panel). Any of these lets the Court pass; all
  three together make this a poor vehicle even for a Justice interested in
  the cap question.
- **Litigant class.** Nevada HOA-sale investors have brought waves of
  enterprise-lien litigation for a decade; the Court has consistently denied
  their petitions. The constitutional-funding wrapper is new; the underlying
  dispute (avoiding the enterprises' liens) is not.
- **No relists yet.** Distributed once pre-BIO (the CFR interrupted that
  conference); the BIO landed July 6, 2026 and the case awaits
  redistribution, so the classic pre-grant relist signal is absent as of the
  July 16 snapshot.

## Base rates and calibration

From the committed statpack (modern discretionary-cert slice,
denial-reweighted): overall Term 2025 grant rate ≈ 2.5%; CA9-originating
petitions grant ≈ 3.0%; zero-relist petitions grant ≈ 0.8%; paid petitions run
above the pooled rate. (This statpack build carries no salience-band table, so
I anchored on the circuit / relist / Term cuts directly.) A called-for
response is historically worth several multiples of the paid baseline — CFR'd
petitions grant at very roughly 8–10% — but this one carries an unusually
strong denial-side bundle: no split, dissent-derived theory freshly rejected
in *CFSA* (7–2) and *Consumers' Research* (6–3), an SG opposition with three
independent vehicle objections, and a litigant class with a long denial
history. I set **P(grant incl. GVR) = 0.05** — meaningfully above the paid-CA9
baseline on the CFR alone, well below the raw CFR rate on the vehicle and
merits-terrain problems. GVR is implausible (no intervening decision to GVR
in light of), so the 0.05 is essentially plenary-grant probability.

**Predicted disposition: denied.** If I am wrong, the likeliest path is a
grant limited to QP1 after several relists, possibly with a dissent from
denial by Justices Alito and/or Gorsuch as the *CFSA* dissenters.

## Inputs used

Provisioned snapshot (`record/snapshots/2026-07-16.json`, docket 25-1144
through the July 6 BIO), `questions-presented.txt`, `petition.txt` (truncated
at ~1/3; QPs, statement, and the core cert-stage argument were within the
provisioned text), and `brief-in-opposition.txt` (complete, 14 pp.).
Retrieval beyond the provisioned inputs is itemized in `retrieval.md`. I did
not search for and did not encounter any disposition of this petition; the
case is live (mode: forward).
