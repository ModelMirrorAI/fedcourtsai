# Patel, et vir v. United States, No. 25-1319 — cert disposition

**Prediction: denied. P(grant, GVR included) = 0.02.**

## The case

Nita and Kirtish Patel pled guilty in 2015 to federal healthcare fraud
(18 U.S.C. § 1347) on stipulated loss figures. A sealed qui tam action under the
False Claims Act, based on the same conduct, was pending when they pled; the
government intervened the day after the pleas, and 31 U.S.C. § 3731(e) plus
collateral estoppel converted the plea admissions into a ~$7.76M FCA summary
judgment. In § 2255 proceedings the Patels argued plea counsel was
constitutionally ineffective for failing to warn of the FCA/collateral-estoppel
exposure. The Third Circuit (Hardiman, J., precedential, 156 F.4th 342) held
that the Sixth Amendment requires advice only on a plea's direct consequences,
declining to extend *Padilla v. Kentucky* beyond deportation — and held **in the
alternative** that even a contrary rule would be a new rule unavailable
retroactively on collateral review under *Edwards v. Vannoy*, 593 U.S. 255, 276
(2021). Panel and en banc rehearing were denied.

## Question presented

Whether the Sixth Amendment protects the right to assistance of counsel
regarding a collateral consequence of a guilty plea, when the consequence is
both sufficiently intertwined with the conviction and sufficiently severe.

## Base rate anchor

From the committed statpack (modern discretionary-cert slice,
denial-reweighted): overall grant rates by Term run 2.5–3.3% (2023–2025 Terms);
CA3-originating petitions grant at 2.9%; petitions never relisted grant at 0.8%.
This is a paid petition (paid petitions grant meaningfully above the blended
paid+IFP rate), filed by competent private counsel, from a precedential opinion
with an en banc denial — a profile somewhat above the raw floor. Start around
3–4%.

## Factors for a grant

- **Genuine doctrinal tension.** The petition frames a split: CA3 (this case)
  and CA7 (*Reeves*) hold collateral consequences categorically outside the
  Sixth Amendment; the en banc Second Circuit (*Farhane*, 121 F.4th 353 (2024))
  and the Eleventh (*Bauder*) read *Padilla* more broadly. The question is
  recurring and important — pleas resolve ~90% of federal convictions.
- **Precedential opinion, rehearing denied en banc** — the kind of considered
  circuit position the Court waits for.

## Factors against (these dominate)

1. **Fatal vehicle problem — the alternative retroactivity holding.** The Third
   Circuit held that even if *Padilla* extended to FCA exposure, that would be a
   new rule barred on collateral review under *Edwards v. Vannoy* (and *Chaidez*
   already held *Padilla* itself non-retroactive). That independent alternative
   ground would sustain the judgment even if petitioners won the question
   presented — the classic reason the Court denies an otherwise cert-worthy
   petition and awaits a direct-appeal or state vehicle.
2. **The split is softer than pleaded.** *Farhane* rests on
   denaturalization-leading-to-deportation — arguably a straightforward
   *Padilla* application, as the CA2 majority itself said — and *Bauder* is an
   affirmative-misadvice case, a distinct doctrinal box. The clean
   failure-to-advise/pure-civil-liability conflict is thin; most circuits have
   only unpublished or fact-bound decisions (*Parrino*, *Tuakalau*, *Santiago*).
3. **The government waived its response** (June 11, 2026). The SG evidently
   sees no threat; a grant would require the Court to first call for a response,
   and nothing on the docket yet signals that interest.
4. **First distribution is to the September 28, 2026 long conference**, with no
   relist and no CVSG — the 0-relist bucket grants at 0.8%, and the long
   conference is historically the least favorable.
5. **Unsympathetic posture.** Convicted healthcare fraudsters collaterally
   attacking decade-old pleas to escape an FCA judgment already affirmed in
   2019; Kirtish's earlier petition (No. 16-1301) was denied in 2017. No amicus
   support appears on the docket as of the snapshot.
6. **No companion vehicle pending.** CourtListener shows no SCOTUS docket for
   *Farhane* (the government did not apparently seek cert from the CA2 en banc
   ruling), so there is no lead case that could produce a hold-and-GVR path;
   GVR probability is negligible.

## Net

The QP is well-crafted and the underlying question will likely reach the Court
eventually, but this petition carries an independent alternative holding that
insulates the judgment, a waived response, a contestable split, and a long-
conference first distribution. I adjust the ~3% paid-petition anchor down for
the vehicle flaw and waiver, and slightly up for the precedential split-side
opinion, landing at **P(grant) ≈ 0.02; predicted disposition: denied**.

Predicted per-justice votes are omitted: cert denials are unsigned and no
justice-level signal (prior dissents from denial on this question) is in the
record.

## Inputs used

- Provisioned snapshot `record/snapshots/2026-07-18.json` (docket 25-1319:
  extension application 25A1098 granted by Justice Alito; petition filed
  Apr 8, 2026 entry; US waiver June 11, 2026; distributed June 17, 2026 for the
  9/28/2026 conference; paid case, Term 2025).
- Provisioned `record/documents/questions-presented.txt` and `petition.txt`
  (240 pp., truncated — the petition body and the appended CA3 opinion through
  its opening section were readable, including the *Edwards v. Vannoy*
  alternative holding at App. 3). No brief in opposition exists (response
  waived).
- Committed `metrics/statpack.md` base rates (disposition, circuit, relist,
  CVSG, per-Term cuts; this statpack version carries no salience-band table).
- Two CourtListener MCP docket searches (Farhane companion check).

**Degradation note:** the cell's corpus query service was unreachable
(`fedcourts query` timed out against the sidecar), so no ranked similar-prior
retrieval was possible; base rates came from the committed statpack instead.
This degrades, not blocks, the cell.
