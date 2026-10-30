# Why P(any grant) = 0.52

**Inputs read.** Snapshot `2026-07-22.json` (cut at the call-for-response day); `questions-presented.txt`; `petition.txt` (truncated at the cap; I read the QPs, the table of contents, the introduction and the legal background). `context.json`: mode `forward`, band `baseline` (sal-v4), distribution_count 1, no CVSG.

**Anchor.** The statpack's sal-v4 "Segment base rate by salience band", `baseline` column, bracketed `reached` rate, pooled over the Term rows strictly before this docket's Term (2025): 2017–2024 run 4.5%–5.9% (n ≈ 1,200–1,750 per Term), about 5.3% pooled. A call for a response raises that some, probably to the low teens for a paid petition with elite counsel (MoFo, plus Morgan Lewis for eight underwriters). But no committed table conditions on the call, so that step is my judgement.

**The decisive adjustment: a pending companion.** The petition asks in the alternative to be held for *Robinhood v. Sodha*, No. 25-944, and says the Ninth Circuit vacated submission of this appeal pending *Robinhood* and decided it in light of that ruling. Forward-mode retrieval (supremecourt.gov dockets for 25-944 and 25-1376) shows:
- The Court called for the SG's views in *Robinhood* on June 1, 2026.
- The SG's October 7, 2026 brief recommends granting *Robinhood*'s first question, reformulated (whether a misleading-omissions claim can rest on materiality without a separate inquiry into whether an affirmative statement was misleading). It recommends denying the second.
- Both petitions are distributed for the November 6, 2026 conference.

ON24's QP 2 matches *Robinhood*'s QP 1. All of this predates the cell run and is legitimate forward signal; it decides the forecast. None of it is this petition's own disposition. Nothing I saw reports this petition as decided.

**Decomposition.**
- P(*Robinhood* granted) ≈ 0.75, given an SG grant recommendation.
- If granted: P(plenary grant of ON24 too, e.g. on the risk-factor QP) ≈ 0.10.
- Otherwise ON24 is held. P(*Robinhood* disturbs the Ninth Circuit) ≈ 0.7, and P(a GVR follows a disturbing ruling) ≈ 0.9.
- If *Robinhood* is denied: about 0.10 that ON24 is granted on the risk-factor split alone. Its vehicle is weak: the decision below is an unpublished memo, and the facts are COVID-era non-renewals.

That gives roughly 0.75 × (0.10 + 0.90 × 0.7 × 0.9) + 0.25 × 0.10 ≈ 0.53. I wrote 0.52. That is far above the band rate, and the gap is entirely the hold-and-GVR path. If the Court instead treats ON24 as distinguishable (its omissions theory runs through risk factors more than through interim financials), the number is too high.

**Other claims.**
- `summary-disposition-route` 0.80: most of the grant mass is a GVR after the hold.
- `relist-increment` 0.97: masked on this moment, and the live docket already shows a further distribution.
- `cvsg-increment` 0.03: the SG has already spoken on the companion.
- `dissent-from-denial` 0.05: a denial after a hold rarely draws a writing. The order-writers values are small to match.

**Where to discount me.** P(*Robinhood* grant) and its eventual direction are the two big unknowns. The hold path also means this event may not resolve until mid-2027. I read the SG brief from PDF-extracted text; I relied on its conclusion and interest sections only.
