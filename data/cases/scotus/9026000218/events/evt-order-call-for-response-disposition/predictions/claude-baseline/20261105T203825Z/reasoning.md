# Reasoning — Matthews v. Louisiana, No. 26-218 (response-requested moment)

**P(any grant) = 0.16; predicted disposition: denied.**

## Inputs read
- Snapshot `record/snapshots/2026-09-30.json` (date cut at 2026-09-30). Docket: paid petition filed Aug 17 2026; four amicus briefs (Innocence Network, Orleans Public Defenders, Cato Institute, fifteen Louisiana Brady exonerees); Louisiana waived response Sep 16; distributed Sep 23 for the 10/9/2026 conference; **Response Requested Sep 29 (due Oct 29)**. One distribution so far, no CVSG.
- `record/context.json`: forward mode, band `baseline` (sal-v7), `cert_anchor.rate` = 0.0515 (10-Term lookback).
- `record/documents/petition.txt` and `questions-presented.txt` (read the QP, introduction, statement and reasons headings). The appendix (243 pp., truncated) was not read in detail. No BIO exists yet — the call for response is what this moment marks; I do not infer what Louisiana will say.
- `same-question.json`: empty list (nothing above the 0.5 threshold).

## Anchor and adjustments
- Anchor: the frozen band rate, 5.2%.
- **Called-for response.** The Court overrode the State's waiver before the first conference. This is a low-bar signal (one Justice or a clerk flag suffices) and most such petitions are denied, but it reliably multiplies the grant-family rate several times over the uncalled population. No committed table conditions on it, so this is judgement.
- **Amici.** Four amicus briefs, including Cato (cross-ideological). The statpack's paid-segment amicus cut puts the 2+ bucket (n=1543) at granted 18.2% + gvr 4.5%; that is a marginal, disposition-time figure and overlaps the response signal, so I do not stack it fully.
- **Posture favouring a grant-family outcome.** The petition is expressly framed as a summary-reversal candidate in the Wearry v. Cain / Smith v. Cain / Kyles line — all Louisiana Brady cases the Court corrected, two of them summarily. Facts as pleaded are strong for materiality: three child/interested eyewitnesses, no physical evidence, suppressed field notes describing a different-looking fleeing man, notes undercutting the key child witness's vantage point, and a non-identifying neutral lineup witness. The trial court is quoted as finding it "undisputed" that discovery was withheld. Elite counsel (Hogan Lovells + SCHR).
- **Against.** This is error correction on a single fact-bound record from a state intermediate court, with a "splitless" QP (the claimed conflict is with how other courts apply the same federal standard). The current Court summary-reverses in favour of state prisoners rarely, and Louisiana's AG will likely defend the ruling as a correct materiality analysis that merely mentioned the strength of the evidence; the courts below may have recited the right standard, which makes the "wrong test" framing contestable. A 30-plus-year-old conviction with prior denials (including No. 20-7311) and a life sentence (non-capital) also lowers urgency. Brown v. Louisiana (2023), cited by the petition, was a denial — the Court has recently declined a similar invitation.

Net: roughly triple the band anchor, to 0.16. Conditional on a grant, I put 0.55 on a summary disposition (per curiam reversal or GVR-like vacatur) versus plenary review, because the petition asks for summary reversal and the Court's Brady corrections of Louisiana have often been per curiam.

## Other claims
- `relist-increment` 0.97: the petition will be distributed again once the response is filed or its time runs (masked for this moment, stated anyway).
- `cvsg-increment` 0.01: state criminal case, no federal interest.
- `dissent-from-denial` 0.30 | denial: Brady cases with a sympathetic record and an amicus-backed summary-reversal ask draw statements/dissents from Sotomayor and Jackson with some regularity; a called-for response suggests at least one chambers is engaged. `order-writers` is consistent: Sotomayor 0.27, Jackson 0.17 (mostly via denial writings), with Thomas/Alito ~0.06–0.07 reflecting dissents if the Court summarily reverses.

## Uncertainty / discount
- I did not read the appendix's lower-court opinions closely, so I cannot confirm how explicitly the Court of Appeal relied on sufficiency language; that is the crux of a summary reversal.
- No retrieval beyond one uninformative corpus query; base rates come from the committed statpack.
