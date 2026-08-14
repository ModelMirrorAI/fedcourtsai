# Reasoning — why P(grant family) = 0.55

## Anchors

- **CVSG cut** (statpack, "Cert petitions by CVSG status (paid scored
  segment)"): among CVSG'd petitions, granted 30.1% + gvr 5.5% ≈ **35.6%**
  grant family, denied 62.0%. This cell's moment is the CVSG, so this is the
  primary anchor.
- **Salience band**: `record/context.json` freezes `band: high` under
  `sal-v2`, matching the segment table's version. Pooling the `high` band's
  bracketed `reached` rates over the Terms strictly before this case's own
  (2017–2024; the 2025 row is this case's Term and is excluded) gives
  ≈ **40%** (weighted over n = 1,059). The two anchors agree on a 35–40%
  starting point.

## Adjustments up (net, to 0.55)

- **The Court's own revealed behavior is the strongest signal.** The petition
  was distributed 12/12/2025, then held ~6.5 months — plainly for *West
  Virginia v. B.P.J.* and *Little v. Hecox* — and on the day it decided those
  cases the Court neither denied nor GVR'd this petition but CVSG'd it.
  *B.P.J.* expressly reserved whether heightened scrutiny applies to
  transgender classifications and said nothing about the *Turner*-in-prisons
  question, so QP1 survived intact, and the CVSG despite a known preservation
  objection (the BIO was on the docket before the first distribution) is an
  affirmative act of continued interest.
- **The SG is likelier than not to recommend a grant.** The federal interest
  is direct (BOP housing and search policy turns on the same standard) and the
  current administration's litigating posture aligns with petitioners. The
  Court follows an SG grant recommendation most of the time; my rough
  decomposition — P(SG recommends grant) ≈ 0.65, P(grant | grant rec) ≈ 0.78,
  P(grant | deny rec) ≈ 0.20 — lands near 0.57.
- **Cert-stage gravity**: a 23-state amicus brief at the petition stage, an
  asserted 3–3 circuit split on QP1 (CA8/CA9/CA10 vs CA2/CA4/CADC), a
  recurring issue flooding lower courts, and the Court's prior GVR of *Fowler
  v. Stitt*, the Tenth Circuit precedent the decision below rests on.

## Adjustments down

- **The vehicle problem is real.** The BIO's lead argument is that petitioners
  never raised the *Turner*-over-*VMI* argument below and affirmatively
  conceded intermediate scrutiny applies; the panel called party presentation
  "decisive," and even the en banc dissent agreed the panel did not decide
  QP1. An unpreserved QP is a classic CVSG-then-deny shape.
- **Interlocutory posture** (motion to dismiss; qualified immunity was granted
  on damages claims below), and QP2 is factbound with no asserted split.
- These keep me at 0.55 rather than the ~0.60 the SG-decomposition alone would
  suggest.

## Label split behind the headline number

Granted (plenary, incl. granted-in-part) ≈ 0.46, gvr ≈ 0.08 (only live if the
SG recommends one), dismissed ≈ 0.01, denied ≈ 0.44. `predicted_disposition:
granted` is the modal label but it is close to a coin flip against denial;
the grant-family probability (0.55) is the number I would defend.

## Claims

- `disposition` 0.55 — restates the above.
- `relist-increment` 0.97 — the docket shows 2 distributions; after a CVSG the
  petition is redistributed once the SG files, so at least one further
  distribution fails to occur only if the case exits first (settlement or
  dismissal, rare).
- `cvsg-increment` 0.01 — a CVSG is already on the docket (2026-06-30); the
  harness masks this claim as vacuous for a CVSG-moment cell.

## Inputs and candor

I worked from the provisioned snapshot (2026-08-14), the petition, BIO, and QP
texts (all fetched with full text), the committed statpack, one corpus priors
query, and forward retrieval (CourtListener + web) about the intervening
*B.P.J.*/*Hecox* decisions — legitimate pre-snapshot public signal for a
forward cell, flagged as decisive context in `flags.json`. Nothing
outcome-revealing about this petition exists (it is pending). Main
uncertainties: the SG's actual recommendation (the single biggest driver, and
months away), and whether the preservation defect leads the Court to wait for
a cleaner vehicle among the several circulating transgender-prison-policy
cases. The corpus priors query was of little use here (see `retrieval.md`),
so the quantitative anchoring rests on the statpack.
