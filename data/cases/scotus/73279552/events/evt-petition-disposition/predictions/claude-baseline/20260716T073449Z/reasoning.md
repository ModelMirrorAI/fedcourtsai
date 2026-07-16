# Calvary Chapel San Jose v. California, No. 25-703 — cert disposition

**Prediction: denied (modal), P(any grant, GVR included) = 0.40.** The single
likeliest disposition is a denial, but the probability of a grant is far above
the ~3% base rate because the docket pattern strongly indicates the petition is
being **held** for *St. Mary Catholic Parish v. Roy*, No. 25-581 (cert granted
April 20, 2026), and held petitions frequently end in a GVR when the lead case
resolves favorably to the petitioner's side.

## The legal question

Calvary Chapel San Jose and Pastor Mike McClure were fined $1,228,700 for
violating Santa Clara County's COVID-era face-covering requirement during
worship services (November 9, 2020 notice of violation through the rule's
rescission on June 21, 2021). The California Court of Appeal, Sixth District,
affirmed in an unpublished decision (Apr. 15, 2025); the Supreme Court of
California denied review (July 16, 2025). The petition (ACLJ, Jay Sekulow,
counsel of record) presents four questions: (1) whether COVID rules with
multiple secular exceptions are not "generally applicable" under *Employment
Division v. Smith* and so trigger strict scrutiny under *Tandon v. Newsom*;
(2) whether church autonomy includes a "liturgical exception"; (3) in the
alternative, whether *Smith* should be overruled; (4) whether the fines violate
the Excessive Fines Clause under *United States v. Bajakajian*.

## Snapshot facts that drive the outcome

1. **The hold pattern (dominant signal).** The petition was distributed once —
   for the Conference of April 24, 2026 — and the snapshot (created July 15,
   2026) shows **no order, no relist, and no reschedule in the ~12 weeks
   since**. A petition considered and denied would show a denial; a relisted
   petition would show fresh "DISTRIBUTED for Conference of …" entries. Neither
   appears. Moreover, the case is still pending *after* the end-of-Term
   cleanup, so it is not being held for an OT2025 merits case; the hold target
   extends into OT2026.
2. **The hold target.** Four days before that conference, the Court granted
   cert in *St. Mary Catholic Parish v. Roy* (25-581), whose first question —
   whether proving lack of general applicability under *Smith* requires
   showing unfettered discretion or categorical exemptions for identical
   secular conduct — is the same doctrinal question as Calvary's QP1. The BIO
   here itself flagged *St. Mary* as the better pending vehicle. Merits
   briefing runs through August 17, 2026, so a decision is expected by ~June
   2027, and this petition's disposition likely waits for it.
3. **Cert-stage salience.** Paid petition; seven cert-stage amicus briefs
   supporting the petition (ADF, Liberty Justice Center, Pacific Justice
   Institute, NRB, Advancing American Freedom, Robertson Center, and West
   Virginia et al. — a multistate brief); experienced Supreme Court counsel.
   Well above the profile of a typical state-court petition.
4. **Vehicle defects (why plenary grant is unlikely and denial stays modal).**
   The decision below is unpublished and uncitable under Cal. R. Ct. 8.1115;
   the challenged rule was rescinded in June 2021 and is unlikely to recur;
   there is no asserted circuit split on QP1 or QP4 — both reduce to factbound
   application of *Tandon* and *Bajakajian*; the "liturgical exception" (QP2)
   was never raised below, creating a serious *Cardinale* preservation/
   jurisdiction problem; and the courts below held in the alternative that the
   face-covering rule would survive strict scrutiny, which blunts the effect of
   any clarification of the general-applicability trigger. The Court has also
   repeatedly declined invitations to overrule *Smith* (*Fulton*; denials in
   *Elim Romanian*, *We the Patriots*), and it just chose *St. Mary* — not this
   case — as its general-applicability vehicle.

## Probability reasoning

Base rates (committed statpack, modern discretionary-cert slice,
denial-reweighted): overall grant ≈ 3%; zero-relist petitions grant at ~0.8%.
On the raw signal cuts this petition has **zero relists**, so a naive read
says deny at ~97%+. But the relist table does not model the hold pattern: a
zero-relist petition that has silently survived ~6+ conferences after a
same-issue grant is not drawn from that bucket. The very act of holding —
rather than denying on April 24 — implies at least several Justices think the
outcome may be affected by *St. Mary*.

Rough tree:

- P(genuinely held for *St. Mary*) ≈ 0.85. Within that branch:
  - *St. Mary* petitioners win on the general-applicability question broadly
    (the Roberts Court's near-unbroken run for free-exercise claimants —
    *Fulton*, *Tandon*, *Carson*, *Kennedy*, *Groff* — plus the United States
    supporting petitioners): ≈ 0.65 → GVR of Calvary ≈ 0.7 (GVR practice for
    held religious-liberty cases is generous, cf. the 2021 wave of COVID
    church GVRs; discounted for the alternative strict-scrutiny holding and
    the factbound comparability findings below).
  - *St. Mary* decided narrowly (e.g., unfettered-discretion grounds tied to
    Colorado's program) or on the *Carson* question only: ≈ 0.2 → GVR ≈ 0.3
    (the *Arlene's Flowers* pattern — held for *Fulton*, then denied when the
    lead case came out narrow — is the live precedent for denial here).
  - *St. Mary* respondents win: ≈ 0.15 → grant-side ≈ 0.05.
  - Branch P(grant incl. GVR) ≈ 0.65·0.7 + 0.2·0.3 + 0.15·0.05 ≈ 0.52.
- P(not a hold — e.g., internal delay, opinion-in-denial in preparation)
  ≈ 0.15 → grant-side ≈ 0.05 (a dissent from denial is likelier than a grant).

Total P(grant, GVR included) ≈ 0.85·0.52 + 0.15·0.05 ≈ **0.45**, which I shade
to **0.40** for the compounding uncertainty in the hold inference and the GVR
propensity. Disposition split: denied ≈ 0.57, **gvr ≈ 0.37**, plenary grant
(incl. granted-in-part) ≈ 0.02–0.03, dismissed ≈ 0.01. "Denied" is therefore
the single likeliest label and drives `granted = 0`, while `probability = 0.40`
carries the elevated grant-side mass. If the grant side materializes, it is far
likelier a **GVR in light of *St. Mary*** (mid-2027) than a plenary grant.

## Timing note

Because the likely path is a hold pending *St. Mary* (argument in OT2026,
decision expected by June 2027), this event will probably not resolve until
roughly June–July 2027.

## Documents consulted

Provisioned inputs: the 2026-07-16 snapshot, `questions-presented.txt`,
`petition.txt` (184 pp., truncated), and `brief-in-opposition.txt` (28 pp.,
complete) — the analysis above anchors on the QPs and weighs the petition
against the BIO. External retrieval (forward mode) is logged in
`retrieval.md`; nothing retrieved concerned this case's own disposition, which
does not yet exist.
