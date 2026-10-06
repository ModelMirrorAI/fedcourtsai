# Rationale for the numbers

**P(grant family) = 0.58; predicted disposition `granted`; claims: disposition 0.58, relist-increment 0.96, cvsg-increment 0.01, summary-disposition-route 0.25 (conditional on grant), dissent-from-denial 0.15 (conditional on denial); big_case_score 0.55.**

## Inputs read

Provisioned snapshot `2026-10-06.json` (11 docket entries; one distribution for the 9/28/2026 conference; CVSG entered 10/5/2026; two amicus briefs for petitioners), `context.json` (mode `forward`, band `high` under `sal-v4`, distribution_count 1, cvsg_date 2026-10-05, term 2025, cut_kind `date`, cutoff 2026-10-06), `event.yaml` (stage `cert`, moment `cvsg`), and all three provisioned documents: the questions presented, the 43-page petition, and the 40-page brief in opposition, each with `empty_text: false` and `truncated: false`. The reply brief is on the docket but was not provisioned.

## Anchors

- **Salience band.** Context freezes `band: high` under `sal-v4`, matching the statpack's band-table version. Pooling the bracketed `reached` figure for `high` over Terms strictly before OT2025 (2017 through 2024, the table's rendered window) gives roughly 35 percent (about 314 of 898 weighted). That is the baseline the evaluator scores skill against.
- **CVSG cut** (paid scored segment): granted 29.4 percent plus gvr 5.5 percent, about 35 percent grant family on 163 resolved. The two anchors agree, so I start at 0.35.

## Adjustments up (to about 0.60)

1. **The Court has already granted this case once**, in October 2023, after a CVSG, and over the SG's recommendation to deny (the BIO itself recounts the SG urged denial on percolation grounds). That is direct evidence that this Court regards the question as worth its time and this case as a workable vehicle. Few CVSG petitions carry that history.
2. **Acknowledged express circuit split** on indistinguishable statutes: the Second Circuit below says in terms that it disagrees with and declines to follow the First Circuit's Conti decision, and the Ninth Circuit (Kivett) sits on the same side as the First. The BIO does not deny the split; it calls it narrow and "1-1," and asks for percolation.
3. **The respondent concedes certworthiness in some vehicle.** The BIO's conclusion asks the Court, if it takes the question, to grant Kivett or Conti and hold this petition. That is an unusual concession: the fight is over vehicle, not whether the Court should act.
4. **Companion CVSG the same day.** The repo's event registry shows an `evt-order-cvsg-disposition` opened 2026-10-05 on Flagstar v. Kivett (No. 25-1350), so the Court called for the SG's views in both the plaintiff-side and bank-side vehicles together, exactly the 2023 pattern (CVSGs in Nos. 22-529 and 22-349) that ended in a grant here and a hold-then-GVR there. A paired CVSG is a stronger signal of intent to decide the question than a lone one.
5. **Stakes and support**: 27 states plus DC and the state bank supervisors as amici; the petition is by experienced Supreme Court counsel; the question has a clean interlocutory posture with no factual disputes.

## Adjustments down (back to 0.58)

1. **Vehicle substitution is the main downside.** The current SG, with the OCC's May 2026 preemption determination and Escrow Powers Rule now final, will almost certainly favor preemption on the merits and may recommend that the Court take the bank-petitioner vehicle (Flagstar) and hold this one. The Kivett respondents have now disclaimed the HOLA vehicle objection that helped this case win the 2023 vehicle contest, and Flagstar arrives on a final judgment with an injunction. If this petition is held behind Flagstar, it is granted (GVR) only if the Court rejects preemption, which I put near even odds given the 2024 opinion's refusal to adopt either side's rule and the new OCC determination weighing the other way.
2. **Percolation argument has a real hook.** No court has addressed the OCC's 2026 actions, and the Court's 2024 footnote expressly reserved the significance of OCC preemption rules. An SG brief recommending denial so lower courts can address the rule first is plausible, and the Court follows SG cert recommendations most of the time, though it did not here in 2023.
3. **Base rates are low for a reason**: even in the `high` band two in three petitions are denied.

Rough decomposition I used: P(Court takes the question this cycle in some vehicle) about 0.75; given that, P(this petition granted plenary, alone or consolidated) about 0.55 and P(held behind Flagstar) about 0.45, with a GVR on roughly half of the held path. That gives about 0.75 × (0.55 + 0.45 × 0.5) ≈ 0.58.

## Other claims

- **relist-increment 0.96.** A CVSG petition is redistributed after the SG files essentially without exception; the residual is withdrawal or settlement.
- **cvsg-increment 0.01.** A CVSG is already on the docket; the harness will mask this claim. A second invitation is nearly unheard of.
- **summary-disposition-route 0.25.** Conditional on a grant, the GVR share is the held-behind-Flagstar-then-vacate path, about 0.15 of total mass against about 0.43 for plenary grant. Summary reversal is negligible.
- **dissent-from-denial 0.15.** Denials following an SG denial recommendation or a hold are rarely accompanied by writings; a statement from Justice Jackson or Sotomayor is the main scenario.
- **big_case_score 0.55.** Stakes are national (14 states' laws, billions in escrow balances, the Dodd-Frank preemption standard, a fresh OCC rule) but the subject is technical and the 2024 decision drew modest public attention.

## Uncertainties and where to discount me

- I could not read the companion dockets' current entries: the CourtListener MCP server returned HTTP 429 (daily rate limit) on every REST call after the two docket searches came back empty, and the companion cases' snapshots are not provisioned on this runner. The paired-CVSG inference rests on the repo's committed event definition for Flagstar (opened 2026-10-05), which is reliable but thin. I did not retrieve the Conti rehearing petition's status beyond what the BIO and petition say.
- I have not seen the reply brief or the amicus briefs' text; my read of the states' and CSBS arguments is from the BIO's characterization.
- The SG's likely cert recommendation is my inference from the OCC's 2026 actions and the administration's posture, not from any filing.
- The corpus `--citation` lookup for the 2024 Cantero decision returned nothing (the column is sparsely filled), so the 2023 history I rely on comes from the petition, the BIO, and general knowledge rather than a corpus row.
- Forward cell: no leakage concern. No search surfaced this petition's disposition.
