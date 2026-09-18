# Reasoning — Winnemucca Indian Colony v. United States, No. 25-1170

**P(grant) = 0.04.** Predicted disposition: denied.

## What I read

- Snapshot `2026-09-17.json` (as-stored, forward mode). Paid petition from the Federal Circuit (No. 24-1108, published at 156 F.4th 1339), docketed April 13, 2026. Proceedings: petition filed Apr 8; SG waiver May 7; distributed May 12 for the May 28 conference; **Response Requested** May 27; two extensions; BIO filed Aug 20; reply Sep 3; distributed Sep 9 for the **September 28, 2026 conference**. No CVSG (impossible here: the SG is the respondent).
- `context.json`: `band: elevated` under `sal-v4`, `distribution_count: 2`, `term: 2025`, `cvsg_date: null`, `signals_observable: true`.
- `documents/`: `questions-presented.txt`, `petition.txt` (32 pp.), `brief-in-opposition.txt` (29 pp.), all with text; none `empty_text`, none truncated.
- `metrics/statpack.md`: modern cert by disposition, relist and CVSG cuts, originating-circuit cut, and the sal-v4 segment base rate by band.

## Anchor

The evaluator's yardstick is the **elevated** band's bracketed `reached` rate pooled over Terms strictly before OT2025. Pooling the eight rendered prior Terms (2017–2024) gives **17.2%** (about 484 grant-family outcomes over n=2810). I take that as the anchor and adjust from it.

Other cuts for shape: the paid-segment relist-count cut reads relist=1 at granted 8.2% + gvr 5.1%; the CVSG cut's `none` bucket reads granted 4.0% + gvr 2.3%; the Federal Circuit bucket reads granted 3.1% + gvr 1.5%. These are terminal-bucket figures, not rates a petition at my state faces.

## Adjustments down (large)

1. **The band is inflated by the docket's shape.** The two distributions bracket a call for response that pulled the petition off the May 28 conference before it was considered. The petition has been considered at zero conferences; the relist-1 / elevated signal, which the anchor prices as a post-conference relist, is here a CFR redistribution. The CFR itself is a real and positive signal (someone in the building wanted the government's view after a waiver), but from general experience of that signal the grant rate among CFR petitions is in the high single digits, not the mid-teens, and this petition is a weak member even of that class. Flagged in `flags.json`.
2. **No split, no cert-worthy framing.** The petition alleges no conflict among the circuits or with this Court. It asks the Court to distinguish Arizona v. Navajo Nation (2023) on a "new water versus existing water" line and to reread Ute Indian Tribe (Fed. Cir. 2024) and Hopi Tribe (Fed. Cir. 2015). Two of the three QPs are error-correction framings. The BIO answers each point cleanly: Winters is a common-law property doctrine and not a treaty, statute, or regulation whose text can impose a duty; 25 C.F.R. 152.22(b) governs conveyance of land and says nothing about water or third-party diversions; Ute's remand left the "general obligation to protect water rights" question open rather than deciding it; Hopi's language is dicta.
3. **Independent jurisdictional bars the Federal Circuit did not reach.** The Court of Federal Claims dismissed the same count under 28 U.S.C. 1500 (a substantially overlapping 2011 Nevada action against the United States was pending when this suit was filed, and the identical 2013 CFC water claim was dismissed on the same ground) and under the 28 U.S.C. 2501 six-year limitations period (the 2013 complaint itself pleaded the diversion). Even a Court interested in the Winters question would face a vehicle in which winning it changes nothing. This is the single strongest reason to sit well below the CFR class rate.
4. **Idiosyncratic facts.** The claim is that BIA's decade-long refusal to recognize either faction in an intra-tribal leadership dispute caused it not to stop a developer's upstream diversion. That is not a fact pattern the Court would choose to make law on.
5. **Petition quality.** Small-firm petition, no amici, QPs poorly drawn (one asks whether the court of appeals "erred"), and the legal argument at points asks the Court to "reconsider" rather than to resolve a question of national importance.

## Adjustments up (small)

- The CFR after a waiver is a genuine above-baseline signal, and the SG answered with a full 29-page BIO rather than a short one, consistent with a chamber having asked seriously.
- Tribal trust doctrine is an area the Court has taken repeatedly (Jicarilla, Navajo I and II, Arizona v. Navajo Nation), Navajo Nation split 5–4, and the Federal Circuit opinion is precedential.
- The BIO's reliance on the CFC's alternative grounds means the Federal Circuit's actual holding could be reviewed without disturbing the judgment only if the Court also took up 1500 and 2501, which cuts back toward denial rather than up.

Net: I land at **0.04**, well below the 17% band anchor and below the paid-segment `none`-CVSG rate, because the vehicle defects are independent of the legal question and the band signal is an artifact of the CFR. I would put roughly a third of the residual grant mass on a plenary grant driven by the Navajo Nation dissenters wanting to police the "no interference" line they read into that decision, and the rest on ordinary noise.

## Claims

- `disposition` 0.04 — same belief as `probability`.
- `relist-increment` 0.22 — from 2 distributions shown. Baseline: most petitions at their first substantive conference are not redistributed. Up from that because the CFR indicates a chamber's interest (a possible statement or a one-conference hold), and because a reschedule at the long conference also counts as a distribution entry under the statpack's own reading of the count.
- `cvsg-increment` 0.01 — the SG is the respondent; a CVSG cannot issue. Near-zero rather than zero only for the resolver's sake.
- `summary-disposition-route` 0.15 — conditional on a grant. No intervening decision supports a GVR and the CA opinion offers no per curiam target, so a grant would almost certainly mean plenary review. The residual reflects the base share of grants that dispose in the cert order and the small chance of a GVR to have the Federal Circuit address the CFC's alternative grounds.
- `dissent-from-denial` 0.06 — conditional on denial. Gorsuch is the only plausible author; the vehicle problems make a writing unlikely.

## Big case score

0.15. Doctrinally live area, but a narrow, fact-bound damages claim by a small tribe with no wider litigation riding on it and two independent jurisdictional bars beneath the question.

## Uncertainty and where to discount me

- I have no statpack cut conditioned on a call for response after a waiver, so the CFR-class grant rate I used is from general knowledge, not a committed figure. If the true CFR-class rate on paid petitions is higher than I believe, my number is too low by perhaps a factor of two, but not by the factor of four that reaching the band anchor would require.
- I did not retrieve the Federal Circuit opinion text beyond the parties' descriptions; both sides agree on what it held, so I do not think this matters.
- Forward cell; CourtListener shows the docket open with no termination date as of today, so nothing here is informed by the outcome.

## Corpus vintage

The corpus priors came from the cell's ranged remote reads (both `fedcourts query` calls logged reads, 10 and 46 GETs). The `--citation` lookup for Navajo Nation returned nothing because only 200 SCOTUS rows carry reporter cites; the `--era 2020s --disposition granted` query returned recent granted priors that were not topically relevant and did not move the number. The statpack read is the committed `metrics/statpack.md`.
