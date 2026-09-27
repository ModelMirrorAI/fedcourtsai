# Reasoning — why P(any grant) = 0.40

## What the cell is

Cert-stage, `moment: arrival`, `forward` mode. Snapshot `2026-09-15.json`: one docket entry (petition filed Sept. 15, 2026; response due Oct. 15, 2026), paid docket, OT2026, from CA2 (No. 26-156, decided Aug. 21, 2026). `context.json` freezes `band: federal` under `sal-v4`, `distribution_count: 0`, no CVSG, `signals_observable: true`. Provisioned documents: `petition.txt` (142 pp., truncated, text extracted) and `questions-presented.txt`. No BIO exists yet. Petitioner is the United States (Solicitor General as counsel of record), so the caption class is `federal`.

## Anchor

The prompt's anchor for a federal arrival cell is the `federal` band's bracketed `reached` rate in the "Segment base rate by salience band (sal-v4)" table, pooled over every Term row shown that precedes OT2026. The table's version matches `context.salience_version`. Pooling the nine rendered Terms (OT2017–OT2025) gives roughly 143 grant-family outcomes over n≈202, about **71 percent**, with per-Term rates ranging from 43.5 percent (OT2018, n=23) to 89.5 percent (OT2022, n=19). The OT2025 row alone is 52.4 percent (n=21). The same band in the whole-slice "Cert petitions by salience band" cut reads granted 48.5 percent plus gvr 22.3 percent, i.e. the grant family is about 71 percent and roughly a third of it is GVRs.

## Why I sit well below the anchor

This petition is not asking to be granted. Its "Reasons for granting" section and its Conclusion ask the Court to **hold** the petition for *United States v. Jackson*, No. 26-304, and then "dispose of it as appropriate." That converts the cert question into a compound of two events in a different docket, so the federal band's pooled rate — which mixes lead SG petitions granted plenary (grants regardless of how the merits come out) with companion GVRs — overstates this cell's odds. A held companion is granted (GVR) essentially only when the government wins the lead case.

My decomposition:

| Branch | Probability | Contributes to grant? |
| --- | --- | --- |
| *Jackson* granted | 0.72 | — |
| … and this petition granted plenary / consolidated | 0.04 | yes |
| … and government wins at least one QP, then GVR here | 0.52 × 0.92 ≈ 0.48 | yes |
| … and government loses, this denied | ≈ 0.48 | no |
| *Jackson* denied, this denied with it | 0.28 | no |
| Rule 46 dismissal / mootness before disposition | folded into the 0.92 | no |

P(any grant) ≈ 0.72 × (0.04 + 0.48) ≈ 0.37; I round up to **0.40** to allow for GVR-type dispositions I cannot enumerate (a partial government win, or a decision in *Jackson* that disturbs the Second Circuit's mootness or Rule 17 analysis). `granted = 0` and `predicted_disposition = denied` because denial is the single most likely label (roughly 0.5) against about 0.36 for `gvr` and 0.04 for plenary `granted`.

Inputs to the branch numbers:

- **P(*Jackson* granted) ≈ 0.72.** For: SG petitioner; three circuits invalidating a longstanding practice; an acknowledged split with the Federal Circuit (*Arthrex*, 2022) on the 3347(a) delegation question; the petition names ongoing disruption to two U.S. Attorney offices in the Second Circuit alone. Against: every court of appeals to reach the first-assistant question has ruled against the government, the Ninth Circuit panel was unanimous with the opinion authored by Judge Miller (retrieved from CourtListener, cluster 10951924), and the Court may regard the problem as one the Executive can cure through nominations. The federal band's high grant rate already prices SG petitions on splits, so I take 0.72 rather than the band rate.
- **P(government wins at least one QP | granted) ≈ 0.52.** The government's textual reading of "the first assistant to the office of such officer" is plausible and backed by 25 years of practice, and a win on either question suffices for a GVR here. But *NLRB v. SW General* (2017) read the FVRA strictly against the Executive, the appellate consensus is 3-0 against, and a textualist former-OSG judge joined it. Close to a coin flip.
- **P(GVR | government wins) ≈ 0.92.** A held SG companion after a government win is almost always GVR'd; the residual covers mootness, a Rule 46 dismissal, or the Court finding the Second Circuit's alternative grounds untouched.

## Corpus priors

`fedcourts query --court scotus --disposition gvr --era 2020s` returned 20 rows (transfer line in `retrieval.md`). Nearly all are companion or hold petitions resolved in the June 29–30, 2026 clean-up order lists after the lead case was decided, with 2–4 distributions each. That matches the shape forecast here — a held petition drawing one initial distribution and one or more redistributions before a Term-end disposition — and is the basis for the relist claim.

## Other claims

- **relist-increment 0.96**: zero distributions on the record; a response is due Oct. 15, 2026, after which distribution follows as a matter of course. Only an early Rule 46 dismissal prevents it.
- **cvsg-increment 0.01**: the SG is the petitioner.
- **summary-disposition-route 0.90** (conditional on grant): the SG asks for hold-and-dispose; plenary consolidation is the small residual.
- **dissent-from-denial 0.10** (conditional on denial): a companion denial after or beside *Jackson* rarely carries a separate writing.

## Stakes

`big_case_score` 0.55. The underlying FVRA questions are significant (control of U.S. Attorney offices; subpoenas directed at the New York AG's investigations of the President and the NRA), but this docket is the companion, not the vehicle, so its own decision would be an order line.

## Where to discount me

- The whole number hinges on two events in another docket that I cannot observe beyond the petition's account and the Ninth Circuit opinion. I did not find *Jackson*'s SCOTUS docket on CourtListener (two lookups returned nothing), so I do not know whether the respondents there have waived or whether a response was requested.
- I read the Second Circuit opinion only through the petition's appendix excerpt and the Ninth Circuit opinion only through its first chunk (caption, panel, staff summary). I did not read the Third Circuit's *Giraud*.
- No BIO exists yet; the New York AG's position on the hold request (and on mootness) is unknown.
- The `federal` band pool is thin (n≈202 over nine Terms) and, more importantly, is the wrong population for a self-declared hold petition; the evaluator scores skill against it regardless, so a large departure from it is the deliberate content of this forecast, not an error.
