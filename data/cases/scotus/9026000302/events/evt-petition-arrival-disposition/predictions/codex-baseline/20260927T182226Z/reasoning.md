# Rationale

## Information set

This is a forward, cert-stage arrival forecast in Isaacson v. National Veterans Legal Services Program, No. 26-302. I read the provisioned `2026-09-09.json` snapshot, the event definition, `context.json`, `documents.json`, the questions presented, and relevant portions of the petition and its reproduced appellate opinion. The September 9 date cut contains the September 3 petition filing, docketed September 8, with a response due October 8, 2026. The frozen state is sal-v4 baseline, Term 2026, zero distributions, and no CVSG. These absences define the arrival moment; they are not negative attention signals.

The petition metadata reports 140 pages and truncation. The question presented, statement, cert arguments consulted, and appellate discussion at Pet. App. 20a–28a are readable, but I do not assume all appendices are available. No opposition is provisioned, and I do not infer waiver, agreement, or weakness from that absence. No subsequent docket state or disposition of this petition was retrieved, and I have no known outcome for it.

## Anchor and adjustment

Isaacson is a private petitioner. The United States is a respondent, not a basis for using the federal-petitioner floor. I use the sal-v4 baseline band's bracketed reached rate, pooling every displayed prior Term, 2017–2025, in the committed statpack. The corresponding unrounded `prefix_est_grant_rate` and `prefix_weighted_resolved` values in `metrics/statpack.json` give 638 grants over a denial-reweighted denominator of 12,720: **5.016%**. This is the private arrival population, not the terminal baseline rate or the zero-relist bucket. The statpack's last modifying commit is dated September 26, 2026; that is artifact vintage, not a verified live-corpus refresh date. No live corpus was queried.

I raise P(any grant) to **22%**, retaining denial as the modal disposition:

- **A concrete legal conflict substantially strengthens the petition.** The QP concerns whether Greenough and Pettus prohibit class-representative service awards absent statutory or rule authorization. The Federal Circuit's reproduced opinion expressly rejects the Eleventh Circuit's interpretation and joins the contrary circuits (Pet. App. 20a–27a). This is more persuasive than an advocate's unsupported split assertion. A limited CourtListener retrieval of Johnson v. NPAS Solutions, LLC, 975 F.3d 1244 (11th Cir. 2020), opinion 4566352, confirms the opposing rule in that opinion's majority discussion, PDF pp. 18 and 26.
- **The question was preserved and decided.** Isaacson objected to the payments as a settlement class member; the appellate court squarely decided their categorical permissibility. The QP isolates that issue from the fee, jurisdictional, and settlement-structure objections described in the petition (petition pp. 1–4; Pet. App. 20a–28a). This supports review without assuming every possible jurisdictional objection is resolved in the petitioner's favor.
- **The record also supplies a substantial defense.** The appellate court distinguishes modest service awards from salary-like historical payments, relies on Rule 23 safeguards, and finds these awards reasonable. It notes that Isaacson does not separately dispute their reasonableness (Pet. App. 24a–28a). The awards are $10,000 to each of three nonprofit representatives within a $125 million settlement. Those facts make the categorical issue clean but reduce the force of an abusive-payment narrative. My adjustment concerns certworthiness, not a conclusion that the petitioner must win on the merits.
- **This need not be the lead vehicle.** The petition itself identifies Isaacson v. Moses, No. 25-1411, as an earlier petition raising the issue (petition pp. 9–10). I did not investigate its current status. That pre-decision fact makes a hold followed by companion treatment plausible, but neither proves review will occur nor warrants assigning its outcome to this petition.

The conflict and national recurrence justify a several-fold increase over the private-petitioner floor; the absence of an opposition, uncertainty about lead-vehicle selection, and the distinction defended in the opinion keep the probability well below one-half. This is a judgmental adjustment, not a fitted likelihood ratio.

## Other probabilities and stakes

**Distribution increment: 98%.** At zero distributions, the declared claim includes the first distribution. It is not a 98% prediction of a true relist after initial consideration. I expect one initial distribution, usually no actual relist, with one further distribution a plausible alternative. The statpack's paid-segment relist cut has 9,892 resolved zero-relist cases, versus 2,486 with one, 482 with two, and 481 with three or more; these terminal buckets inform shape, not a forward hazard estimate.

**CVSG increment: 2%.** The statutory and class-action question does not appear to require a separate invitation, particularly with the United States already a respondent represented in the snapshot by the Solicitor General. An ordinary government response is not a CVSG. The statpack's 163 resolved CVSG cases versus 13,178 without a CVSG provides only terminal context, not this case's conditional probability.

**Summary route given any grant: 35%.** Plenary treatment remains likelier conditional on grant, but the identified companion creates a meaningful hold-and-GVR possibility. No intervening controlling decision is established in the materials consulted; immediate summary reversal is not my central forecast. **Separate writing given denial: 10%.** An express circuit disagreement creates some chance of a statement, but an unexplained denial is the modal prediction. I do not forecast individual cert votes.

**Stakes: 0.58.** A nationwide rule for class-representative compensation would affect settlement design across many fields. The specific legal issue is nevertheless narrower than the underlying PACER-fee dispute or total settlement value.

## Retrieval limitations

An official-site web search for general certiorari standards and two attempts to open the Court's rules page returned no usable content. No proposition is attributed to those failed calls. CourtListener successfully supplied the narrow Johnson precedent check. The provisioned appellate opinion remains the main counterweight to the petition's advocacy; missing opposition and petition truncation limit confidence rather than prevent a forecast.
