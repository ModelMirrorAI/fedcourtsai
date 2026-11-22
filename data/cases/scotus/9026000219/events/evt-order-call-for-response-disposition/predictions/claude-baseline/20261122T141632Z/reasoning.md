# Reasoning — Johnson v. United States, No. 26-219 (response-requested moment)

**P(grant) = 0.04; call: denied.**

## What I read
- Snapshot `2026-09-15.json`: paid petition from the Court of Appeals for the Armed Forces (CAAF No. 25-0202, judgment May 26, 2026), filed Aug 17, 2026; the United States waived its response Aug 31; distributed Sep 2 for the Sep 28 conference; **response requested Sep 14** (due Oct 14). One distribution, no CVSG, no amicus briefs.
- `petition.txt` and `questions-presented.txt` (13-page petition by Air Force appellate defense counsel). I skimmed the appendix listing only; I did not read the CAAF opinion in full and rely on the petition's description of it (majority affirmed on the good-faith exception; Chief Judge Ohlson dissented, calling the search an unconstitutional fishing expedition).
- `context.json`: band `baseline` (sal-v8), `cert_anchor.rate` 0.0518, amicus line (arm `none`) 0.0269. `same-question.json` lists no matching petitions.
- Forward-mode check of the Court's live docket page: after my snapshot, the Solicitor General obtained two extensions; the response is now due Dec 7, 2026. No response filed, no disposition. Nothing there changes the picture beyond timing.

## Anchor and adjustments
- Anchor: the frozen baseline-band reached rate, ~5.2%. The zero-amicus reference line is ~2.7% (a floor, since briefs could still arrive, though I expect none).
- **Up:** the Court called for a response after the government waived. At least one chambers thought the petition deserved an answer. No committed table conditions on this; my own judgment is that a call for a response roughly doubles a bare waived-response paid petition's chances (which sit near 1%), putting such petitions in the mid-to-high single digits on average. There is also a dissent below from CAAF's chief judge, and sympathetic facts (seven months of phone content searched; the prosecutor conceded no nexus).
- **Down:** 
  - The petition alleges **no conflict** among courts. It cites civilian circuit cases only for the proposition that consulting an attorney is relevant to good faith. The issue (commander-issued search authorizations under Mil. R. Evid. 311/315) is unique to the military system, so no split can develop, and the Court takes CAAF cases very rarely — and almost never on a servicemember's petition raising an evidentiary/Fourth Amendment application question.
  - The question as framed would require a categorical rule unsettling a long-standing structural feature of military practice (commander authorizations), or else it collapses into fact-bound error correction of one good-faith ruling. Both are poor cert candidates.
  - The petition is short and thinly developed; no amicus support.
  - The government will oppose, and the SG's oppositions in military cases are usually effective. Two extensions suggest an ordinary BIO, not a confession of error.
- Net: the call for a response and the weak-vehicle factors roughly offset; I land slightly below the band anchor at 0.04.

## Other claims
- `relist-increment` 0.97: the petition must be redistributed once the response is in (masked on this cell anyway). Residual is withdrawal/dismissal.
- `cvsg-increment` 0.003: the United States is the respondent; a CVSG is essentially impossible.
- `summary-disposition-route` 0.20 (conditional on grant): no pending case I know of would support a GVR, and summary reversal of CAAF is rare; but a grant here would be unusual enough that a non-plenary route (e.g., SG concession leading to GVR) carries real conditional weight.
- `dissent-from-denial` 0.06: the response call shows some interest, and Justices Sotomayor, Gorsuch and Jackson have written on Fourth Amendment and military-justice denials; still, most called-for-response denials draw no writing.

## Uncertainty / where to discount me
- I do not know which chambers prompted the call or why. I have not seen the government's response (not yet filed) and do not infer its content.
- The uplift for a called-for response is my estimate, not a committed base rate.
- The corpus query I ran returned generic granted priors, not informative for this case; it did not shape the number.
