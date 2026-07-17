# Mendenhall v. City and County of Denver, No. 25-1205 — cert disposition

**Prediction: denied. P(grant, GVR included) = 0.06.**

## The question presented

The petition asks the Court to overrule *Jones v. United States*, 362 U.S. 257
(1960), and hold that the Fourth Amendment's "Oath or affirmation" requirement
means a witness with firsthand knowledge must swear before the issuing
magistrate — i.e., that hearsay cannot supply probable cause for a warrant. It
is a pure originalist overruling ask (built on Sacharoff, *The Broken Fourth
Amendment Oath*, 74 Stan. L. Rev. 603 (2022)), analogizing to *Crawford* and
*Ramos* as precedents where the Court restored a categorical textual guarantee
over a balancing regime.

## Posture and record facts (from the snapshot and provisioned documents)

- Paid petition (Term 2025 docket, No. 25-1205), filed April 16, 2026, out of
  an **unpublished** Tenth Circuit affirmance (No. 25-1081, Jan. 16, 2026) of a
  Rule 12 dismissal. Petitioner is represented by the Institute for Justice.
- Civil vehicle: a § 1983 **Monell** claim against Denver alleging a municipal
  policy of authorizing hearsay-based warrant applications; the search warrant
  for Mendenhall's townhouse rested on a double-hearsay affidavit (detective
  swore to what another officer relayed of the complainant's story). Both
  courts below held the claim squarely foreclosed by *Jones* and said any
  change must come from the Supreme Court.
- **Four cert-stage amicus briefs** (Walker & Young — Breonna Taylor-adjacent
  plaintiffs; Law Enforcement Action Partnership; Law Scholars via Gibson
  Dunn; Civil Rights Attorneys), an unusually strong show of support.
- Distributed for the June 18, 2026 conference; on **June 15 the Court called
  for a response** (Denver had waived), due July 15. The BIO was submitted
  July 14. The case has not yet been redistributed post-BIO; no relist yet.

## Base rates (committed statpack, denial-reweighted modern cert slice)

- Modern discretionary-cert grant rate: ~3% (367 granted of ~11.7k resolved);
  recent Terms 2.5–3.3%.
- Originating CA10: granted 5.0%.
- Relist cuts: 0 relists → 0.8% grant; 1 relist → 7.6%; 2 → 33.6%. No relist
  has occurred yet here, but the June 15 **call for a response** is a
  chambers-attention signal of comparable strength to an early relist: at
  least one Justice engaged enough to pull the petition off the conference
  track and demand adversarial briefing. (The statpack has no CFR cut; its
  CVSG cut — 27.1% grant — is a much stronger and inapposite signal, since a
  CVSG requires a Court order and this is a mere staff-level response request.)
- Paid (not IFP) filing, which sits above the pooled rate.

Starting from ~3–5% and crediting the CFR, the amicus interest, and expert
counsel, an uninformed structural estimate would sit near 8–10%.

## Case-specific discount

Three features pull the estimate back down:

1. **No split, and none possible.** Every circuit is bound by *Jones*; the
   petition candidly presents no conflict, only "importance" and "wrongness."
   The Court almost never grants a first-ask frontal overruling petition
   without prior percolation in its own separate opinions — *Crawford* and
   *Ramos* each followed years of Justice-level criticism of *Roberts* and
   *Apodaca*. I searched CourtListener for any SCOTUS opinion engaging the
   Sacharoff oath thesis or a firsthand-knowledge oath rule and found none:
   no sitting Justice has publicly questioned *Jones*'s hearsay holding.
2. **Seismic reliance interests.** The entire modern warrant apparatus —
   informant tips, *Aguilar/Spinelli*, *Gates* totality review, officer
   summary affidavits — rests on *Jones*. Adopting the rule would invalidate
   routine practice in every jurisdiction; even Justices sympathetic to
   Fourth Amendment originalism will hesitate to take that up on this record.
3. **Vehicle defects the BIO presses.** Under *Board of County Commissioners
   v. Brown*, Monell liability requires deliberate indifference; a
   municipality that conformed its warrant practice to binding Supreme Court
   precedent arguably cannot be liable even if *Jones* were overruled — so the
   judgment may not turn on the question presented. The decision below is
   also unpublished and cursory (7 pages).

The most likely trajectory: redistribution in late summer, possibly a relist
or two reflecting a chamber drafting a statement respecting denial or a
dissent from denial (Thomas or Gorsuch are the natural authors), then denial.
A GVR is essentially unavailable — there is no intervening decision.

## Bottom line

The CFR and amicus attention make this much stronger than a typical paid
petition, but a no-split, first-ask request to overrule a load-bearing
66-year-old precedent on a contested Monell vehicle is still a heavy
underdog. **P(grant) = 0.06; predicted disposition: denied.** Confidence 0.6
(the unresolved post-BIO relist behavior is the main unobserved variable; a
double relist would move me to ~0.15–0.20).

## Big-case score

0.7 — if granted and decided on the merits this would be a landmark
restructuring of warrant practice nationwide, and the petition already draws
Breonna Taylor / FISA framing, four amicus briefs, and IJ's media reach. The
stakes are high even though the grant odds are low.

## Inputs used

Provisioned snapshot (`record/snapshots/2026-07-17.json`), questions
presented and full petition text (`record/documents/`), the committed
`metrics/statpack.md`. The BIO's text was **not** provisioned
(`documents.json` lists only petition and QP) even though the filing appears
on the docket July 14; since this is a `forward` cell with unrestricted
retrieval I fetched the BIO PDF from supremecourt.gov and extracted its text
— the vehicle analysis above relies on it. Corpus `fedcourts query` returned
zero rows for every topic tried (see `retrieval.md`), so qualitative priors
come from general legal knowledge rather than corpus neighbors.
