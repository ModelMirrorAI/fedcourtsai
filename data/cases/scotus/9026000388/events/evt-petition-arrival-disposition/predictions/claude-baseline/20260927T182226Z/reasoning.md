# Rationale for the numbers

**P(grant) = 0.24; predicted disposition denied.**

## Anchor

Arrival-moment cert cell (`moment: arrival`, `stage: cert`), forward mode, snapshot
`2026-09-23.json`, cut by date at 2026-09-23. `context.json` freezes `band: baseline` under
`sal-v4`, which matches the statpack's segment table heading. Petitioners are 48 private
individuals; respondents are private companies; no sovereign appears in the caption, so the
caption class is `private` and the anchor is `baseline`'s bracketed `reached` rate pooled
over the Terms strictly before OT2026 that the table renders (OT2017–OT2025). Weighting each
Term's reached rate by its `n` gives roughly 5.0% (≈637 grants over ≈12,720 reached
petitions; the Term rates run 3.9%–5.9%). I did not use the relist-count cut's relist-0
figure (1.2%), which is the rate among petitions that ended undistributed and understates an
arrival's prospects, and I did not use the Eighth Circuit origin row (1.2% granted) as an
anchor, since it pools IFP and unselected petitions.

## Adjustments up (dominant)

- **Counsel.** Jenner & Block with Ian Gershengorn (a former Acting Solicitor General) as
  counsel of record. Petitions from this tier of the Supreme Court bar are granted at rates
  well above the baseline band.
- **Decision below.** Published Eighth Circuit opinion, 2–1, with a dissent on the exact
  question presented (Judge Grasz), en banc rehearing denied. A published divided opinion is
  the classic pre-grant shape.
- **Asserted split.** *Nahno-Lopez v. Houser* (10th Cir. 2010, joined by then-Judge Gorsuch)
  states that allottees have "a federal common-law trespass claim"; *Davilla v. Enable
  Midstream* (10th Cir. 2019) adjudicates one on materially identical facts (pipeline,
  expired right-of-way, individual allottees). The Ninth Circuit authority (*Agua Caliente*
  1971, *Milner* 2009) is older and less squarely on point. The panel below acknowledged the
  tension and tried to explain it away, which is itself evidence the split is real enough
  to be taken seriously.
- **United States' position.** The government filed an amicus brief in the Eighth Circuit
  supporting the allottees and rejecting the precise distinction the panel drew; the panel
  gave it "no deference or separate consideration." That sharply raises the probability
  that a CVSG, if called, returns a recommendation to grant, and raises the grant
  probability directly.
- **Vehicle.** Pure legal question, pressed and passed on at every stage, case-dispositive,
  no disputed facts, a single clean QP.
- **Cross-ideological appeal.** The right-to-exclude framing (*Cedar Point*) speaks to the
  Court's property-rights wing; the Indian-law framing (*Oneida*, *Poafpybitty*) to Justice
  Gorsuch and the Court's liberal members.

## Adjustments down

- **The base rate is unforgiving.** Even petitions with all of the above are denied more
  often than not.
- **Split is contestable.** The BIO will argue the Tenth Circuit assumed the cause of action
  without deciding it and that the Ninth Circuit cases concern jurisdiction and standing;
  the Court may prefer to let the question percolate despite petitioners' claim that the
  three circuits hold 99% of individual allotments.
- **Alternative remedies.** The United States is asserting federal common-law trespass and
  ejectment counterclaims on the allottees' behalf in the parallel *Tesoro* APA case, and
  the BIA administrative trespass process exists (it once awarded $187 million before
  reversing itself). Respondents will say the allottees are not remediless, which softens
  the "property in name only" pitch.
- **Federal common law.** The Court's general reluctance to recognize or extend federal
  common-law causes of action could make some Justices hesitant, though here the cause of
  action is one the Court itself recognized in *Oneida II*.
- **Government's current view is unknown.** The supportive amicus brief was filed in January
  2024 under a different administration. If the current Solicitor General does not stand
  by it, the CVSG channel becomes a risk rather than a boost.
- **Arrival-moment uncertainty.** No BIO, no conference. I am forecasting before any
  docket signal exists, so the number carries more spread than a distribution-moment
  forecast would.

Decomposing: roughly P(CVSG) 0.35 × P(grant | CVSG) ≈ 0.55, plus P(no CVSG) 0.65 ×
P(grant | no CVSG) ≈ 0.10, gives ≈ 0.26. I shade to 0.24 to respect the low anchor and the
unknown BIO.

## Claims

- `disposition` 0.24 — equals the top-level probability.
- `relist-increment` 0.95 — the snapshot shows zero distributions; almost every paid
  petition that is not withdrawn or dismissed is distributed at least once. The residual is
  a Rule 46 dismissal after settlement before conference.
- `cvsg-increment` 0.35 — see above; Indian-law trusteeship cases draw CVSGs at well above
  the paid-docket rate (~1%), and the government has already taken a side, but the Court
  may treat the existing brief as sufficient.
- `summary-disposition-route` 0.07 — conditional on a grant; no intervening decision to
  GVR against, and a reasoned published opinion with a dissent is not a summary-reversal
  candidate.
- `dissent-from-denial` 0.15 — conditional on a denial; a Gorsuch statement or dissent is
  plausible given his *Nahno-Lopez* history and his Indian-law writings, but separate
  writings on denial remain uncommon.

## Big-case score

0.38. Significant to Indian country and to pipeline operators crossing allotted land; the
question recurs; but the doctrine is technical and the case would not be a marquee argument.

## Inputs used and their standing

- Snapshot `2026-09-23.json`: three docket entries (extension application, grant, petition
  filed). No BIO, no distribution, no CVSG — as the arrival moment defines.
- `documents.json`: petition fetched (179 pages, `truncated: true`, text extracted) and the
  QP section. No brief in opposition exists yet. I read the QP, introduction, statement of
  the case, and Reasons II–IV in full; Reason I (the *Oneida* argument) I skimmed via the
  introduction's summary.
- `metrics/statpack.md`: modern-cert disposition table, originating-circuit cut, relist and
  CVSG cuts, per-Term table, and the sal-v4 segment table for the anchor.
- Corpus `fedcourts query` (see `retrieval.md`): the granted/2020s filter returned mostly
  emergency-docket applications and a list of recent plenary grants with their distribution
  counts, which confirmed the shape (granted paid petitions typically show 2–5
  distributions) but gave no Indian-law comparator. No adjustment rests on it.
- CourtListener MCP: confirmed both Eighth Circuit *Chase v. Andeavor* opinions (2021 and
  January 30, 2026) are indexed as published; found no SCOTUS docket for 26-388 and no
  pending petition in *Bad River Band v. Enbridge*, so no companion case bears on this one.
  I did not read the Eighth Circuit opinion text itself; my account of the panel's
  reasoning comes from the petition and is therefore the petitioner's characterization.

## Where to discount me

The two most decision-relevant unknowns are the BIO's vehicle arguments (especially the
*Tesoro* counterclaims) and the current Solicitor General's view. If the BIO shows the
allottees' claims are effectively being litigated by the United States in *Tesoro*, the
grant probability should drop toward 0.12–0.15; if the government files or signals support
at the cert stage, it should rise toward 0.40. I also have not independently verified the
split beyond the petition's quotations of *Nahno-Lopez* and *Davilla*.
