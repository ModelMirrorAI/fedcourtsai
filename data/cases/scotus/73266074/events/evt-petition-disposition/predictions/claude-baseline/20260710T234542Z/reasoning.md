# Hastings College Conservation Committee v. California, No. 25-1231 — cert disposition

**Prediction: denied. P(granted) = 0.06.**

## The case

Petitioners — an alumni association and descendants of Serranus Clinton
Hastings — challenge California's AB 1936 (2022), which renamed Hastings
College of the Law to "College of the Law, San Francisco," legislatively
declared that S.C. Hastings "perpetrated genocidal acts" against the Yuki
people, and eliminated the 1878 Act's reservation of a Board seat for
Hastings' heirs. The California Court of Appeal (First District, published,
115 Cal. App. 5th 272) affirmed dismissal on demurrer, resting the contract
holding solely on the reserved powers doctrine and rejecting the bill of
attainder claim; the California Supreme Court denied review on January 28,
2026. The petition (docketed April 29, 2026) presents two questions:

1. **Contract Clause** — whether the 1878 Act, which conditioned the
   college's founding on Hastings' $100,000 payment and promised the name
   "forever" and the Board seat "always," created contractual obligations a
   later legislature cannot impair; petitioners argue the court below
   misread *United States v. Winstar Corp.*, 518 U.S. 839 (1996), and
   *Fletcher v. Peck*, because at minimum a damages/restitution remedy
   survives the reserved powers doctrine.
2. **Bill of Attainder** — whether legislation posthumously declaring an
   individual a perpetrator of crimes and stripping statutory benefits from
   him and his descendants is an attainder, a question the Court has not
   addressed on the merits since *Selective Service System v. MPIRG* (1984).

## Signals for grant

- **Call for response.** Both respondents waived on May 27, 2026. The
  petition was distributed for the June 25 conference, and on June 22 the
  Court **requested a response** (due July 22; respondents' extension motion
  was submitted July 10, the snapshot date). A CFR means at least one
  chambers wants the case examined; empirically it lifts a paid petition's
  grant odds roughly an order of magnitude above the ~1% baseline, into the
  high single digits. It also means the petition was *not* denied at the
  conference it was first distributed for.
- **Doctrinal novelty.** The bill of attainder question is genuinely
  undeveloped (no merits decision in 40+ years) and framed in historical
  terms (Coke, founding-era posthumous attainders) that could interest the
  current Court's originalist wing. The Contract Clause question — whether
  reserved powers defeat even a *damages* remedy despite *Winstar* — has
  broader significance for public-private naming-rights and donation
  agreements.
- **Clean-ish legal posture.** Demurrer dismissal, published opinion, pure
  questions of law; petitioners plausibly argue the decision conflicts with
  the reasoning of seven Justices in *Winstar* (plurality + Scalia
  concurrence).

## Signals for denial (dominant)

- **No split.** The petition alleges no conflict among circuits or state
  high courts on either question — Rule 10's core criterion. Its "Reasons"
  are error-correction ("conflicts with this Court's jurisprudence") plus
  importance, historically a weak cert posture.
- **Weak vehicle.** The judgment comes from an *intermediate* state
  appellate court after discretionary review was denied — a rare source of
  grants. The strongest doctrinal hook (damages survive under *Winstar*)
  was held **waived** below, so it arrives wrapped in an
  adequate-and-independent-state-ground fight; the petition spends pages
  litigating *Cruz v. Arizona*/*Lee v. Kemna* just to reach it. The
  attainder claim has a standing wrinkle (the attainted man died in 1893;
  heirs assert derivative reputational and statutory injuries).
- **Fact-bound.** Both questions turn on one idiosyncratic 1878 California
  statute; a decision would resolve little beyond this dispute, and
  *Winstar* itself was a fractured plurality, making "conflict with this
  Court's jurisprudence" contestable.
- **No supporting ecosystem.** No amicus briefs on the docket as of the
  July 10 snapshot, small-firm counsel rather than the repeat SCOTUS bar,
  and a politically sensitive subject (a state's atonement measure for
  atrocities against Native Americans) with little institutional pressure
  to intervene.

## Base rates

The committed statpack's overall SCOTUS resolved base rate (granted 1.4%,
denied 4.4%, other 78.4% of 296 resolved) blends merits-era labels and
understates modern cert selectivity; the "Modern discretionary-cert" cut
the predict prompt points to is absent from the current statpack (flagged).
The corpus cohort of petitions distributed for the same June 25, 2026
conference (via `fedcourts query --era 2020s`) shows the familiar pattern:
of eight sampled, seven denied, one granted. Modern paid petitions are
granted at roughly 3–4%; conditioning on a call for response raises that to
roughly 8–10%.

## Weighing

Start near the CFR-conditioned prior (~8–10%), then discount for the
absence of any split, the intermediate-state-court source, the state-law
waiver/vehicle problems on the best question, and the fact-bound record —
none of which the CFR cures. The novelty of the attainder question and the
Court's occasional appetite for historical one-offs keep the tail
non-trivial. I land at **P(granted) ≈ 0.06** and predict **denied** — most
likely after the response and any reply circulate, at or after the
long conference opening October Term 2026.

## Retrieval degradation note

The configured CourtListener MCP server failed on every call with a
server-side configuration error (session store unavailable), so no
CourtListener retrieval informed this prediction; I proceeded on the
provisioned snapshot, the petition/QP text, the statpack, and `fedcourts
query` corpus priors. Details in `retrieval.md` and `flags.json`. I have no
knowledge of this petition's actual outcome (it post-dates my training
data), and I did not seek it.
