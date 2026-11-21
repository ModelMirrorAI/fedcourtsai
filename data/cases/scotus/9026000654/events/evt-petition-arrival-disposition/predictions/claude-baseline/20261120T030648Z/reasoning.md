# Reasoning — City of Daytona Beach v. Scott, No. 26-654 (arrival cell)

**P(grant) = 0.02; call: denied.**

## What I read
- Snapshot `2026-11-20.json`: paid petition filed Nov 16 2026, docketed Nov 19; response due Dec 21. No distribution, no response, no amici (the arrival moment by definition).
- `questions-presented.txt`; `petition.txt` (truncated at the cap: I saw the statement and only the opening page of the Reasons for Granting — the pipeline cut note falls inside the petition's own argument, so the rest of the argument is unknown to me, not absent); `decision-below.txt` (11th Cir., published, Newsom J. for Newsom, Brasher, Tjoflat; I confirmed it is the June 25, 2026 judgment the petition describes); `lower-court-docket.txt` (rehearing en banc sought and denied Aug 17 2026, no dissent noted in the entries read).
- `same-question.json`: empty list — no pending or decided petition matched on the question text.

## Anchor
`context.json` freezes band `baseline` (sal-v8) with `cert_anchor.rate` = 0.0517 (reached-rate, ten prior Terms). The petitioner is a city, which the caption rule places in the private/baseline class, so that floor is the right arrival anchor. The amicus line for the `none` arm is 0.027 — a floor-ish reference since briefs could still come. The statpack amicus cut (0 briefs: granted 1.9% + gvr 1.8%, n=11,188 resolved) is consistent.

## Adjustments (net downward to ~2%)
- **No real split shown.** The panel treated the city's out-of-circuit authorities (5th Cir. *National Federation of the Blind v. Arlington*, 3d Cir. *Mazo*, 9th Cir. *Project Veritas*) as distinguishable, and post-*Reed* courts have fairly uniformly held panhandling-specific rules content-based. The first QP heading itself argues that the law "remains uncertain", not that circuits conflict. The portion of the petition I could read cites pre-*Reed* cases.
- **Poor vehicle.** The Eleventh Circuit vacated in part and remanded for plaintiff-by-plaintiff standing findings and to re-scope the injunction under *Trump v. CASA*; the case is interlocutory in substance. The ordinance also failed strict scrutiny on tailoring, a fact-bound alternative hurdle, and QP3 (is traffic safety compelling?) would not change the result because the panel assumed the interests were arguably compelling.
- **QPs are loosely framed** (QP2 asks "how closely" a definition must track *Austin*), and counsel is a solo practitioner rather than a repeat Supreme Court advocate.
- **Unanimous panel, no en banc dissent**, opinion by a judge whose First Amendment writing the Court's majority tends to credit.
- **Upward:** a government petitioner, a published opinion invalidating a municipal law, and the *Reed*/*Austin* boundary is a question some Justices care about; homelessness-related regulation has drawn recent attention. A GVR is conceivable only if some intervening content-neutrality decision lands; I know of none pending that controls.

## Other claims
- `relist-increment` 0.97: the record shows zero distributions; virtually every paid petition is distributed at least once. The residual is a Rule 46 dismissal or other pre-distribution exit.
- `cvsg-increment` 0.003: no federal interest.
- `summary-disposition-route` 0.30 (conditional on grant): if anything happens here, a GVR/summary route is a substantial share, but with no identified intervening case I stay below the historical cert-order share of grants.
- `dissent-from-denial` 0.02 and the `order-writers` numbers: separate writings on denials are rare; Thomas/Alito are the likeliest to say anything about *Reed*/*Austin*.

## Where to discount me
The petition's argument section was mostly cut, so a split argument I could not see may exist. No BIO exists yet. Retrieval was limited to one corpus query and the statpack; I made no CourtListener or web calls.
