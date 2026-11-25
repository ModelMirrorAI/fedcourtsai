# Reasoning — scotus/9026000515 (No. 26-515, Jones v. United States), evt-petition-disposition

**P(grant) = 0.006; call: denied.**

## What I read
- Snapshot `2026-11-25.json`: paid petition from the Federal Circuit (No. 2024-2053, decided Apr 24 2026, rehearing denied Jul 13 2026), filed Oct 12 2026; the United States **waived** its response on Nov 13; distributed Nov 24 for the Dec 11, 2026 conference. One distribution, no relist, no CVSG, no call for a response, no amicus briefs.
- `questions-presented.txt`, `petition.txt` (37 pp., complete) and the opening of `appendix.txt` (the Federal Circuit opinion; the appendix row is truncated, and I read only the appellate opinion's opening pages). No brief in opposition exists (waiver). No `decision-below.txt` was staged; I used the petition's own appendix.
- `context.json`: band `baseline` (sal-v9), `cert_anchor.rate` 0.0518, `cert_amicus_line` (arm `none`) 0.0269. `same-question.json` lists no similar petitions.

## Anchor and adjustments
- Anchor: the frozen baseline-band reached rate, 5.2%. The no-amicus arm puts it at 2.7%. The statpack relist cut for petitions that end with no relist is 1.8% grant family (n=10,311 resolved); the Federal Circuit bucket is 4.6% grant family (n=888).
- I go far below these because of features specific to this petition:
  1. **Response waived, none requested.** The Court essentially never grants without a response; a grant would first need a call for a response, and nothing on the docket shows one. This alone puts the petition in the weakest part of the baseline band.
  2. **Nonprecedential decision.** The Federal Circuit opinion (Taranto, joined by Lourie and Dyk) is marked nonprecedential. The petition's importance argument — that the ruling will "bind" federal investigators and cripple crime-scene practice — is undercut by that, and the Solicitor General, the supposed victim of the rule, declined even to respond.
  3. **No split.** The petition claims conflict with this Court's plain-view cases (Warden v. Hayden, Horton, Coolidge) and cites one Eighth Circuit case; it does not develop a square circuit conflict. It is an error-correction request.
  4. **Odd posture / vehicle.** The Fourth Amendment question arises only derivatively, as a reason the FBI's failure to take the officer's Glock was not spoliation, inside a treaty "bad men" damages suit in which the Claims Court then held a trial and found the family had not proved the officer fired the fatal shot. The question is embedded in a discretionary sanctions ruling, and its effect on the judgment is uncertain.
  5. Petitioners are private parties represented by non-specialist counsel; no amici.
- Residual 0.6% covers a call for a response followed by unexpected interest, or a hold/GVR I cannot foresee.

## Other claims
- `relist-increment` 0.04: a further distribution would mostly come from a call for a response (after which the petition is redistributed) or a reschedule; both are uncommon for a waived petition of this kind.
- `cvsg-increment` 0.001: the United States is the respondent, so a CVSG is not the mechanism; the Court would call for a response instead.
- `summary-disposition-route` 0.30 (conditional on a grant): if anything happened here, a GVR or summary action is plausible relative to plenary review, roughly in line with the cert-order share of grants; I have no intervening decision in view.
- `dissent-from-denial` 0.006 and `order-writers`: a noted dissent or statement is very unlikely; the slightly higher numbers for Gorsuch and Sotomayor reflect their interest in Indian-law and police-accountability matters, nothing in the record.

## Uncertainty and caveats
- The statpack's band table is headed sal-v8 while my context froze the band under sal-v9. I used the frozen `cert_anchor` (and the baseline floor, which is also my caption class's floor as a private petitioner); noted in `flags.json`.
- I did not read the Claims Court opinion in the appendix beyond what the petition and the appellate opinion's opening describe, so my vehicle assessment rests on the petition's own account of the Fourth Amendment ruling.
- No CourtListener or web retrieval was used; one corpus query returned generic recent denials that did not inform the number.
