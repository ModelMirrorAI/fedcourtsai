# Rationale — P(grant) = 0.17

## What I read

Provisioned inputs: the snapshot `record/snapshots/2026-10-06.json` (seven docket entries through the October 5, 2026 BIO), `record/context.json` (forward mode, `band: baseline` under `sal-v4`, `distribution_count: 1`, no CVSG, Term 2025, paid), `event.yaml` (cert stage, `moment: distribution`), and all three provisioned documents: `questions-presented.txt`, `petition.txt` (42 pages, full text), and `brief-in-opposition.txt` (45 pages, full text). `documents.json` reports none truncated and none `empty_text`. Base rates from the committed `metrics/statpack.md`.

## Anchor

The context's band is `baseline` and the statpack's band table is labelled `sal-v4`, matching `salience_version`, so the table is a valid anchor. Pooling the bracketed `reached` figures for `baseline` over the eight Terms strictly before this case's Term (OT2017–OT2024, every Term the table renders before OT2025) gives a weighted **5.1%** grant-family rate on n ≈ 11,580 weighted resolved petitions. The relist-count cut (paid scored segment) puts a once-distributed petition that ends there at about 1.7% grant family, and the CVSG cut's `none` row at about 6.3% — consistent with the band anchor. The OT2025 row is this case's own Term and excluded.

## Adjustments up (from 5% to the high teens)

1. **Response requested.** Respondents waived on July 6; the Court called for a response on July 21, after the petition had been distributed. The salience band does not key on this, so it is signal beyond the anchor. A call for a response means some chambers wanted to see the opposition before voting, and it is a necessary step before any summary reversal; in paid cases it roughly doubles or triples the grant likelihood relative to the undistinguished pool.
2. **Genre fit.** A published Ninth Circuit opinion reversing a grant of qualified immunity to police officers on the strength of a single circuit precedent (United States v. Johnson, 2001), with an **eight-judge dissent from denial of rehearing en banc** (Judge Collins) saying the panel defined clearly established law at too high a level of generality. The Court has summarily reversed the Ninth Circuit in exactly this posture several times (Stanton v. Sims — itself a hot-pursuit-of-a-misdemeanant yard entry — Sheehan, Kisela, Rivas-Villegas), and the petition cites a 2026 per curiam (Zorn v. Linton) as showing the practice continues; I could not verify that citation (see retrieval note below) and weigh it as the petition's characterization.
3. **Support and stakes.** A municipal and law-enforcement amicus coalition including IMLA filed at the petition stage, and the petition expressly asks for Rule 16 summary reversal, which is the realistic grant route.

## Adjustments down

1. **The BIO is strong on the vehicle.** Counsel (ICAP at Georgetown) frame the record in the light most favorable to respondents, as Tolan requires at summary judgment: Officer Rose chose not to chase; eighteen minutes elapsed before the K-9 arrived, then a briefing, a records check, and a loudspeaker announcement; the sweep ran one to three hours; the dog detects a fear hormone and does not track; Rose called the perimeter a "total failure"; the suspect was never found. On those facts, Welsh v. Wisconsin arguably clearly establishes the violation even without Johnson, and the panel also rested on Lange's misdemeanor-exigency point as an independent ground the petition does not squarely attack. A summary reversal on disputed facts is the kind the dissenters resist, and the Court is choosier about vehicles than the en banc dissent count alone suggests.
2. **No split, fact-bound QP1, forfeited QP3.** The petition identifies no circuit conflict; question 1 is the application of a settled standard to one record; question 3 (only this Court's decisions clearly establish law) was not raised below and is uniformly rejected by the circuits. None of these is a plenary-grant driver.
3. **Petition quality.** The questions presented are long and argumentative, the petition is by regional insurance-defense counsel rather than a Supreme Court specialist, and its argument leans heavily on quoting the dissental. Not disqualifying, but it is not the polished vehicle that usually earns a per curiam.
4. **Pace of QI summary reversals.** The Court issues only a handful of qualified-immunity per curiams per Term, and fewer in recent Terms than in 2014–2018; most CFR'd QI petitions from officers are still denied.

Net: 5.1% × roughly 2.5 (response requested) × roughly 1.7 (genre, dissental, amici) × roughly 0.75 (BIO's vehicle attack and the absence of any split) ≈ 16–17%. I report **0.17**.

## Claims

- `disposition` 0.17 — as above.
- `relist-increment` 0.96 — the snapshot shows one distribution; the BIO arrived October 5, so a redistribution for a November conference is all but certain. The residual is dismissal or withdrawal before redistribution (a settlement) or a parse quirk.
- `cvsg-increment` 0.02 — no federal interest.
- `summary-disposition-route` 0.65 (conditional on grant) — the grant case is the per curiam error-correction pattern the petition itself asks for; plenary review on a Lange follow-on is the minority route given the disputed record. For comparison the baseline band's terminal grant family in the statpack splits roughly one-third `gvr` to two-thirds `granted`, but that `gvr` share reflects held-case GVRs after a merits decision, a route unavailable here, and the `granted` label does not separate per curiam summary reversals from plenary grants — so the cut is shape, not a lookup.
- `dissent-from-denial` 0.12 (conditional on denial) — a response request plus an eight-judge dissental raise the odds that a Justice writes on denial above the ordinary few percent, but dissents from denial in officer-loses QI cases remain uncommon.

## Uncertainty and where to discount me

- The response request's weight is the crux. If the request came from a Justice who wanted to see the BIO before voting to summarily reverse, 0.17 is too low; if it was a routine clerk-pool request on a petition with a dissental, it is too high. I cannot tell which from the docket.
- I could not read the Ninth Circuit's amended opinion or the Collins dissent directly; my account of both is reconstructed from the parties' competing descriptions. Both sides agree on the core holding (no hot pursuit; Johnson clearly established the violation) and on the eight-judge dissental.
- **Retrieval was degraded.** Both CourtListener MCP calls returned HTTP 429 (daily quota exhausted, roughly an hour to reset), so I did not verify Zorn v. Linton, the amended opinion's text, or whether the Court has granted any comparable petition this Term. `fedcourts query` returned no priors with `--disposition summary-reversal` and its citation filter is unpopulated for SCOTUS rows, so corpus priors contributed nothing beyond the statpack.
- `big_case_score` 0.3 reflects stakes if decided, not grant odds: a per curiam or denial here is a narrow event; only an (unlikely) plenary grant on question 1 or any engagement with question 3 would make this a widely followed case.
