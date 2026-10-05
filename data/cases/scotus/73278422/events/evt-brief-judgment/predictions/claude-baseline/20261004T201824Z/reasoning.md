# Rationale for my numbers

**P(judgment disturbed) = 0.86. Judgment: reversed. Lineup 6–3.**

## Mode and inputs

Forward merits cell, `moment: briefed`, `cut_kind: date`, cutoff 2026-09-24. I read the provisioned snapshot `record/snapshots/2026-09-24.json` (the docket through the respondent's merits brief filed September 23, 2026), `record/context.json`, the event definition, and all five provisioned documents: the petition, the questions presented, the brief in opposition, `merits-brief-petitioner.txt` (86 pages, filed August 14, 2026), and `merits-brief-respondent.txt` (74 pages, filed September 23, 2026). Both merits briefs fall inside the cutoff, as a briefed cell's should, so this forecast is made on the parties' own merits arguments and not on the docket skeleton alone. The Solicitor General's amicus brief supporting petitioner (filed August 21) and the state and other amici are on the docket but not provisioned; I know their content only as both parties characterize it. No argument transcript exists yet.

## Anchor

The statpack's "The merits docket (granted cases)" section publishes an `excluded` column, so it is quotable. Certiorari was granted June 22, 2026, so the grant Term is OT2025 and the pool is grant Terms 2015–2024. The table renders rows only for 2017–2024 (Terms without a parsed judgment are omitted), so the pool I can compute is those eight rows:

| pool | parsed | disturbed | rate |
| --- | --: | --: | --- |
| grant Terms 2017–2024 | 516 | 360 | 69.8% |

That clears the 30-parsed-judgment floor comfortably. Coverage: 2024 shows 73 parsed of 75 granted and 2023 shows 55 of 55, so the nearest Terms are not badly censored; the pack-level 69.8% (n=540) includes OT2025 and is not my anchor. The context's `band: high` is a cert construct about a grant that already happened; I did not use it, as the stage rule says.

## Adjustments up from 0.70

- **The Court's record.** Petitioner's brief counts thirteen refusals to extend Bivens in 45 years, and Goldey v. Fields (2025) was a unanimous summary reversal of a Fourth Circuit Bivens extension in the prison setting. No Bivens plaintiff has won in this Court since Carlson itself. A grant at the behest of the defendant officer, supported by the Solicitor General as amicus (with divided argument sought) and by nineteen States, in a case where eleven Ninth Circuit judges dissented from denial of rehearing en banc, is the classic reversal posture.
- **The doctrinal path is already paved.** Abbasi held that "potential special factors that previous Bivens cases did not consider" make a context new, and specifically identified alternative remedies and post-Carlson legislation as such factors in a case the Court called parallel to Carlson. Egbert held that an alternative remedial structure alone forecloses the remedy. The majority need only apply those two sentences. Watanabe's concession that he loses at step two if the context is new removes the vacate-and-remand route and sharpens the result toward outright reversal.
- **Hold-then-grant.** The petition was distributed in January, rescheduled twice, held through the spring with supplemental briefs in February and May, then granted June 22, the day before Cisco Systems v. Doe came down. The Court did not GVR or summarily reverse, so it wants to write; given the composition, what it writes is far more likely to confine Carlson than to reaffirm it.

## Adjustments down

- **This is Carlson's heartland.** Unlike every post-1980 Bivens case the Court has decided, the right (Eighth Amendment), the mechanism (deliberate indifference to a serious medical need), the defendant class (federal prison staff), and the forum (a BOP facility) all match the recognized context. The respondent's brief is strong on this: the Davis footnote that a cause of action does not depend on "the quality or extent" of injury, the Abbasi dictum that the Abbasi plaintiffs' injuries were "just as compelling" as Carlson's, and the point that the ARP was created in 1974, before Carlson, so it is not a factor that post-dates the precedent. The last point is a genuine factual problem for petitioner's "not considered" argument and may push the majority to lean on the PLRA rather than the ARP.
- **Ratification.** The Westfall Act's express carve-out for constitutional torts and the PLRA's exhaustion requirement written in response to McCarthy v. Madigan are the best stare decisis arguments a Bivens plaintiff has ever had, and the Court's own Cisco Systems footnote ("this far and no further", reaffirming the three historic ATS torts on reliance grounds) shows the current majority is willing to leave a residual judge-made remedy standing. That is why I put the probability of an outright overruling of Bivens or Carlson near zero, and it is also why affirmance is not negligible: Roberts, Kavanaugh, or Barrett could conclude that holding this claim a "new context" is overruling Carlson in all but name.
- **Vacatur risk.** If the Court reformulates the new-context inquiry (for example, rejecting a per se ARP rule but requiring courts to weigh severity and immediacy), it might vacate and remand instead of reversing. That changes the judgment label but not the disturbed binary.

My rough decomposition: reversed 0.80, vacated 0.05, affirmed-in-part 0.01 (together 0.86 disturbed); affirmed 0.12; DIG or equally divided 0.02.

## Votes

The six-Justice Egbert majority against the three Egbert dissenters is the modal outcome, and I give it roughly 0.65; the next most likely lineups are a 7–2 or 8–1 reversal if Kagan or Jackson accept the new-context holding on the strength of Abbasi, and a 5–4 either way with Roberts or Barrett crossing. The writing roles I committed to are the two I think most forecastable: a Gorsuch concurrence calling to overrule Bivens (he wrote exactly that in Egbert) and a Sotomayor dissent (she wrote the Egbert dissent). I left the majority author unstated. The vote block is banked, not scored today.

## Semantic claims

My `majority-ground` proposition is that the holding rests on the ARP-plus-PLRA special-factor theory from Abbasi and Egbert, rejects ratification, and leaves Carlson formally intact. The live alternative is a holding resting principally on the severity and immediacy differences petitioner leads with; I think the majority will mention those but not rest on them, because a life-versus-injury line invites exactly the case-by-case litigation Egbert tried to end. My `ground-breadth` proposition is categorical because the factors I expect the Court to rely on are system-wide; if the Court instead rests on severity, the ground would be narrower and my breadth claim would be wrong independently of the ground claim.

## Where to discount me

I have not read the Solicitor General's brief or any amicus brief, and I have not seen the reply brief or the argument. The ARP-predates-Carlson point was new to me from the respondent's brief and I may be underweighting how much it troubles the Chief Justice and Justice Barrett. The CourtListener docket-entries endpoint returned nothing for this docket, so I could not confirm whether respondent-side amici or any other post-cutoff filing changes the picture. No information about this case's disposition surfaced in any retrieval; the judgment does not yet exist.
