# Rationale — claude-baseline, evt-order-judgment (moment: grant), run 20260816T173750Z

**P(disturbed) = 0.73; judgment = reversed; 6–3.**

## Mode and inputs

Forward-mode merits cell at the grant moment. I worked from the provisioned
snapshot (docket through the 2026-08-12 CIRCULATED entry), the provisioned
petition and questions-presented text, and the provisioned
`brief-in-opposition.txt` — which in fact concatenates two filings: the
cert-stage BIO (Nov 10 2025) **and** respondents' merits brief (Jul 27 2026,
truncated at 112 pages). So I had respondents' merits advocacy in text;
petitioners' merits brief (filed May 14 2026) is recorded on the docket but not
provisioned and I did not retrieve it, so my read of petitioners' merits-stage
framing is inferred from their cert petition. The docket records the case
argued-not-yet (set for October 5, 2026) with the full amicus fleet on file.
This is a forecast made on the granted docket plus cert-stage petition text and
respondents' merits brief — not on both sides' merits briefing.

## Anchor

The committed statpack's "The merits docket (granted cases)" section publishes
an `excluded` count (67), so it is quotable and is the registered baseline.
Pooling disturbed over parsed across the ten grant Terms strictly before this
case's (grant term OT2025; the pack holds Terms 2017–2024 in that window):
359/515 ≈ **0.697**, comfortably past the 30-parsed floor. Coverage caveat
quoted per the pack: the rate covers the parsed slice only (515 parsed against
557 granted in the window), and the nearest Terms' parsed slices are the most
pendency-censored, skewing toward quicker dispositions.

## Adjustments from 0.697 to 0.73

**Up:**
- The Court granted this interlocutory case after six distributions, having
  denied review of the same litigation twice before (No. 20-783, GVR'd on the
  removal question; No. 21-1550, denied 2023), and with the finality objection
  led in the BIO. Granting over that hurdle signals appetite to decide, and the
  Court reverses what it goes out of its way to take — especially a state
  supreme court ruling in a nationally contested area where every lower-court
  merits ruling has gone against the industry (there is nothing to "affirm and
  settle"; the split is between the state-court consensus and petitioners).
- The United States filed a voluntary cert-stage amicus (no CVSG) supporting
  petitioners, filed on the merits for petitioners, and moved for divided
  argument — SG-supported petitioners win at rates well above the base rate.
- 26 states and the full business-amicus establishment support petitioners; the
  current majority's revealed skepticism of state-law regimes with nationwide
  or extraterritorial reach cuts the same way.

**Down:**
- The grant order **added a jurisdictional question** (statutory + Article III)
  sua sponte. Respondents' merits brief leads with it: the Colorado judgment is
  interlocutory, § 1257 finality requires Cox's fourth exception, and ASARCO's
  Article III theory arguably fails on a non-final order. A dismissal for want
  of jurisdiction or a DIG leaves the judgment below standing. I put ~0.15
  here — material, but bounded, because the Court granted with the objection
  squarely presented and denial was the cheaper way to duck.
- Affirmance (~0.10): respondents' displacement argument (after AEP, no federal
  common law remains to preempt, and Ouellette permits source-state law) has
  won in every court to consider it, and Thomas's and Gorsuch's hostility to
  free-floating implied preemption gives it a nonzero path.
- Equally divided affirmance (~0.02): Alito took no part in No. 21-1550 (this
  same litigation, 2023); if he is recused and one conservative defects, 4–4 is
  live. The snapshot's grant order notes no recusal, so I cannot confirm his
  participation either way.

Decomposition behind 0.73: reversed 0.58, vacated 0.13, in-part 0.02
(disturbed = 0.73); affirmed 0.10, jurisdictional dismissal/DIG 0.15, equally
divided 0.02 (undisturbed = 0.27).

## Votes and semantic claims

The 6–3 lineup follows the majority's federalism/preemption pattern; the main
vote uncertainties are Alito's participation (above) and whether Gorsuch or
Thomas writes separately to cabin the preemption rationale (I forecast a
Gorsuch concurrence). Authorship (Roberts) is a low-confidence forecast and,
like all writing roles, unscored today. The semantic claims commit to the
constitutional-structure/federal-common-law ground and a categorical breadth;
the honest alternative ground — CAA obstacle preemption — is meaningfully less
likely for this majority, which has been cutting back purposes-and-objectives
preemption.

## Where to discount me

- I did not read petitioners' or the SG's **merits** briefs (not provisioned;
  I kept retrieval minimal), so my forecast of the majority's precise ground
  leans on the cert petition's framing plus respondents' merits brief's
  characterization of it.
- The salience band in `record/context.json` (`high`) is a cert construct;
  per the stage rules I did not anchor on it.
- My one corpus `query` (citation lookup for AEP) returned nothing — the
  citation column covers only 161 of 590k SCOTUS rows — so no corpus priors
  inform the number; the anchor is the statpack alone.
- The Alito-recusal read rests on my background knowledge of the 2023 denial
  in No. 21-1550, which I could not verify from the provisioned record.
